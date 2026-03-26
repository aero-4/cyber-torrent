from src.auth.domain.entities import TokenData
from src.core.redis import get_redis_client
from src.utils.datetimes import get_timezone_now


class RedisTokenStorage:

    def __init__(self):
        self.redis = get_redis_client()

    async def is_active_token(self, jti: str) -> bool:
        return await self.redis.exists(f'tokens:{jti}')

    async def add_store_token(self, token_data: TokenData) -> None:
        key = f"tokens:{token_data.jti}"
        total_seconds = int((token_data.exp - get_timezone_now()).total_seconds())  # because need int seconds

        await self.redis.setex(name=key, value=token_data.sub, time=total_seconds)
        await self.redis.sadd(f"user_tokens:{token_data.sub}", token_data.jti)

    async def remove_tokens_user(self, token_data: TokenData) -> None:
        token_keys_jti = await self.redis.smembers(f"user_tokens:{token_data.sub}")  # get all jti user
        for jti in token_keys_jti:
            await self.redis.delete(f'tokens:{jti}')  # revoke jti - access or refresh

        await self.redis.delete(f"user_tokens:{token_data.sub}")
