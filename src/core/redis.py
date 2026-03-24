from redis.asyncio import Redis


def get_redis_client():
    return Redis()