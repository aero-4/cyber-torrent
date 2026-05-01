import json
from datetime import timedelta

from src.core.infrastructure.redis import get_redis_client
from src.games.domain.entities import Game, GamesCollection
from src.games.infrastructure.db.uow import GamesUnitOfWork
from src.games.infrastructure.services.redis_cache import RedisCache
from src.games.presentation.dtos import GamesCollectionDTO
from fastapi.encoders import jsonable_encoder

cache = RedisCache()


async def collect_games(data: GamesCollectionDTO) -> GamesCollection:
    uow = GamesUnitOfWork()

    collection_key = ":".join([str(i) for i in data.model_dump(exclude_none=True).values()])
    games = await cache.get_cache_object(collection_key)

    async with uow:
        count = await uow.games.get_count_games(data)

        if not games or games['total_count'] != count:
            games: GamesCollection = await uow.games.get_all(data)
            await cache.save_cache_object(collection_key, games)

    return games


async def get_game(slug: str) -> Game:
    uow = GamesUnitOfWork()
    game = await cache.get_cache_object(slug)

    if not game:
        async with uow:
            game = await uow.games.get_by_slug(slug)
            await cache.save_cache_object(slug, game)

    return game
