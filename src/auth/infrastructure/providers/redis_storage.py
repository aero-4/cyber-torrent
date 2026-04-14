from src.auth.domain.entities import TokenData
from src.auth.domain.interfaces.token_auth import ITokenStorage
from src.core.config import config
from src.core.infrastructure.redis import get_redis_client
from src.utils.datetimes import get_timezone_now


class RedisTokenStorage(ITokenStorage):

    def __init__(self):
        self.redis = get_redis_client()

    async def is_active_token(self, jti: str) -> bool:
        return await self.redis.exists(f'tokens:{jti}')

    async def is_valid_token_email(self, email: str, token: str | int) -> None | str:
        email_storage: str = await self.redis.get(f"email:{token}")
        email_storage = str(email_storage.decode("utf-8"))
        return email_storage if email_storage == email else None

    async def add_store_token(self, token_data: TokenData) -> None:
        key = f"tokens:{token_data.jti}"
        total_seconds = int((token_data.exp - get_timezone_now()).total_seconds())  # because need int seconds

        await self.redis.setex(name=key, value=token_data.sub, time=total_seconds)
        await self.redis.sadd(f"user_tokens:{token_data.sub}", token_data.jti)

    async def add_email_token(self, email: str, token: str | int, expire_seconds: int = config.email.TWO_FACTOR_TOKEN_EXPIRE_SECONDS) -> None:
        key = f"email:{token}"
        await self.redis.setex(key, value=email, time=expire_seconds)

    async def remove_tokens_user(self, token_data: TokenData) -> None:
        token_keys_jti = await self.redis.smembers(f"user_tokens:{token_data.sub}")  # get all jti user
        for jti in token_keys_jti:
            await self.redis.delete(f'tokens:{jti}')  # revoke jti - access or refresh

        await self.redis.delete(f"user_tokens:{token_data.sub}")
