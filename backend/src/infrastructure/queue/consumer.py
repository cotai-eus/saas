import json
import logging
import time
from uuid import UUID

from infrastructure.cache.redis_client import get_redis_client
from infrastructure.database.session import SessionLocal
from infrastructure.database.models.message import Message as MessageModel
from infrastructure.database.models.channel import Channel as ChannelModel
from infrastructure.database.mappers import channel_from_orm, message_from_orm
from infrastructure.providers.factory import ProviderFactory

logger = logging.getLogger(__name__)

QUEUE_NAME = "messages.outbound"
DELAYED_QUEUE = "messages.delayed"
POLL_INTERVAL = 1
MAX_RETRIES = 3
BASE_DELAY = 5
MAX_DELAY = 300


def _backoff(attempt: int) -> int:
    delay = min(BASE_DELAY * (2 ** (attempt - 1)), MAX_DELAY)
    jitter = int(delay * 0.1)
    import random
    return delay + random.randint(0, jitter)


def _flush_delayed(client) -> None:
    now = time.time()
    jobs = client.zrangebyscore(DELAYED_QUEUE, 0, now)
    for job in jobs:
        if client.lrem(QUEUE_NAME, 0, job) == 0:
            client.rpush(QUEUE_NAME, job)
        client.zrem(DELAYED_QUEUE, job)


def process_job(data: dict) -> None:
    message_id = data["message_id"]
    channel_id = data["channel_id"]

    db = SessionLocal()
    try:
        msg_row = (
            db.query(MessageModel)
            .filter(MessageModel.id == UUID(message_id))
            .first()
        )
        if not msg_row:
            logger.error("Message %s not found", message_id)
            return

        channel_row = (
            db.query(ChannelModel)
            .filter(ChannelModel.id == UUID(channel_id))
            .first()
        )
        if not channel_row:
            logger.error("Channel %s not found", channel_id)
            return

        if channel_row.status != "active":
            logger.warning("Channel %s not active, skipping", channel_id)
            msg_row.status = "failed"
            msg_row.error_message = "Channel not active"
            db.commit()
            return

        channel = channel_from_orm(channel_row)
        message = message_from_orm(msg_row)
        provider = ProviderFactory.get(channel.type)

        result = provider.send(channel, message)

        if result.success:
            msg_row.status = "sent"
            msg_row.provider_message_id = result.provider_message_id
            db.commit()
        else:
            _handle_failure(db, msg_row, result.error_code, result.error_message)
            db.commit()
    except Exception:
        logger.exception("Failed to process message %s", message_id)
        db.rollback()
    finally:
        db.close()


def _handle_failure(db, msg_row, error_code, error_message) -> None:
    msg_row.status = "failed"
    msg_row.error_code = error_code
    msg_row.error_message = error_message


def run_worker(once: bool = False) -> None:
    client = get_redis_client()
    logger.info("Worker started, polling queue=%s", QUEUE_NAME)

    while True:
        _flush_delayed(client)

        raw = client.blpop(QUEUE_NAME, timeout=POLL_INTERVAL)
        if raw is None:
            if once:
                break
            continue

        _, payload = raw
        data = json.loads(payload)
        attempt = data.get("attempt", 1)

        try:
            process_job(data)
        except Exception:
            logger.exception(
                "Job failed (attempt %d/%d): %s",
                attempt,
                MAX_RETRIES,
                payload,
            )
            if attempt < MAX_RETRIES:
                data["attempt"] = attempt + 1
                delay = _backoff(attempt)
                client.zadd(DELAYED_QUEUE, {json.dumps(data): time.time() + delay})
                logger.info(
                    "Requeued message %s with attempt %d in %ds",
                    data.get("message_id"),
                    attempt + 1,
                    delay,
                )
            else:
                logger.error(
                    "Job exhausted retries (%d/%d): %s",
                    attempt,
                    MAX_RETRIES,
                    payload,
                )

        if once:
            break
