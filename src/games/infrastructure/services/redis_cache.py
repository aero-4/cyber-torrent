import json
from datetime import timedelta

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from src.core.infrastructure.redis import get_redis_client


class RedisCache:

    def __init__(self):
        self.redis = get_redis_client()

    async def get_cache_object(self, key: str) -> dict | None:
        cached_item = await self.redis.get(key)

        if not cached_item:
            return None

        return jsonable_encoder(
            json.loads(cached_item)
        )

    async def save_cache_object(self, key: str, obj: BaseModel):
        await self.redis.setex(key,
                               timedelta(minutes=10),
                               json.dumps(obj.model_dump(mode="json")))
