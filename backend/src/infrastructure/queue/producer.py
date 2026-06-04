import json
import logging
from functools import lru_cache

from infrastructure.cache.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class QueueProducer:
    def __init__(self):
        self.client = get_redis_client()

    def publish(self, queue: str, data: dict) -> None:
        self.client.rpush(queue, json.dumps(data))
        logger.info("Published job to queue=%s data=%s", queue, data)


@lru_cache
def get_producer() -> QueueProducer:
    return QueueProducer()
