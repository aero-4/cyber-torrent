from redis.asyncio import Redis

from src.auth.domain.entities import TokenData
from src.core.redis import get_redis_client
from src.utils.datetimes import get_timezone_now


class RedisTokenStorage:

    def __init__(self):
        self.redis = get_redis_client()

    async def is_active_token(self, token_data: TokenData) -> bool:
        return await self.redis.exists(f'tokens:{token_data.jti}') == 1

    async def set_token_jti(self, token_data: TokenData) -> None:
        key = f"tokens:{token_data.jti}"

        total_seconds = (token_data.exp - get_timezone_now()).total_seconds()

        await self.redis.setex(name=key, value=token_data.sub, time=total_seconds)
        await self.redis.sadd(f"user_tokens:{token_data.sub}", token_data.jti)


    async def remove_tokens_user(self, token_data: TokenData) -> None:
        token_keys_jti = await self.redis.smembers(f"user_tokens:{token_data.sub}")
        for jti in token_keys_jti:
            await self.redis.delete(f'tokens:{jti}')

        await self.redis.delete(f"user_tokens:{token_data.sub}")
