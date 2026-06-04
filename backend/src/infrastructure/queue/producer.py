import json
import logging
from typing import Any, Dict

from infrastructure.cache.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class QueueProducer:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = get_redis_client()
        return self._client

    def publish(self, queue: str, data: Dict[str, Any]) -> None:
        try:
            self.client.rpush(queue, json.dumps(data))
            logger.info("Published job to queue=%s data=%s", queue, data)
        except Exception as e:
            logger.error("Failed to publish to Redis queue=%s: %s", queue, e)
            # Try to reconnect once
            self._client = None
            try:
                self.client.rpush(queue, json.dumps(data))
                logger.info("Published job to queue=%s after reconnection", queue)
            except Exception as e2:
                logger.critical("Final failure publishing to Redis: %s", e2)
                raise


def get_producer() -> QueueProducer:
    return QueueProducer()
