import json
import logging
from typing import Optional, Any
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger("transit.redis")

redis_pool: Optional[aioredis.Redis] = None

async def init_redis_pool():
    global redis_pool
    try:
        redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=2.0
        )
        await redis_pool.ping()
        logger.info("Successfully connected to Redis cache instance.")
    except Exception as e:
        logger.warning(f"Redis connection failed, continuing in-memory/degraded mode: {e}")
        redis_pool = None

async def close_redis_pool():
    global redis_pool
    if redis_pool:
        await redis_pool.close()
        logger.info("Redis cache connection closed.")

async def get_cached(key: str) -> Optional[Any]:
    if not redis_pool:
        return None
    try:
        data = await redis_pool.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Error reading from Redis key '{key}': {e}")
    return None

async def set_cached(key: str, value: Any, ttl_seconds: int = 86400):
    if not redis_pool:
        return
    try:
        serialized = json.dumps(value, ensure_ascii=False)
        await redis_pool.set(key, serialized, ex=ttl_seconds)
    except Exception as e:
        logger.warning(f"Error writing to Redis key '{key}': {e}")
