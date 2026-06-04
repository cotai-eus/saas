from functools import lru_cache

from infrastructure.settings import settings


try:
    import redis as _redis

    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False


@lru_cache
def get_redis_client():
    if not _REDIS_AVAILABLE:
        raise RuntimeError(
            "redis-py is not installed. Install with: pip install redis"
        )
    return _redis.from_url(settings.redis_url, decode_responses=True)
