from redis.asyncio import Redis

from src.core.config import config


def get_redis_client():
    return Redis(host=config.redis.REDIS_HOST,
                 port=config.redis.REDIS_PORT)
