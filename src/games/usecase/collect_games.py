import json
from datetime import timedelta

from src.core.infrastructure.redis import get_redis_client
from src.games.domain.entities import Game, GamesCollection
from src.games.infrastructure.db.uow import GamesUnitOfWork
from src.games.presentation.dtos import GamesCollectionDTO
from fastapi.encoders import jsonable_encoder


async def collect_games(dto: GamesCollectionDTO) -> GamesCollection:
    uow = GamesUnitOfWork()
    redis = get_redis_client()
    collection_key = ":".join([str(i) for i in dto.model_dump(exclude_none=True).values()])
    cached_games = await redis.get(collection_key)
    if cached_games:
        return jsonable_encoder(json.loads(cached_games))

    async with uow:
        games: GamesCollection = await uow.games.get_all(dto)
        await redis.setex(collection_key,
                          timedelta(minutes=30),
                          json.dumps(games.model_dump(mode="json")))

    return games


async def get_game(slug: str) -> Game:
    uow = GamesUnitOfWork()
    async with uow:
        game = await uow.games.get_by_slug(slug)
    return game


async def get_games_by_category(category: str):
    uow = GamesUnitOfWork()
    async with uow:
        games = await uow.games.get_by_cat(category)
    return games
