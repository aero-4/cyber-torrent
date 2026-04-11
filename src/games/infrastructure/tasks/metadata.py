import asyncio
import logging
from datetime import timedelta

from src.core.infrastructure.redis import get_redis_client
from src.games.domain.entities import GameCreate, GameImageCreate
from src.games.infrastructure.db.uow import GamesUnitOfWork
from src.torrents.infrastructure.db.repositories import PGTorrentsRepository
from src.torrents.infrastructure.db.uow import TorrentsUnitOfWork
from src.torrents.infrastructure.services.metadata_loader import MetadataParser
from src.torrents.infrastructure.tasks.torrent import searcher_torrents

redis = get_redis_client()


async def searcher_games() -> None:
    metadata = MetadataParser()
    uow = GamesUnitOfWork()

    page = await redis.get("metadata_page")
    page: int = int(page) + 1 if page else 1

    logging.info(f"RAWGIO: Metadata page: {page}")
    games_result = await metadata.search(page)
    success = 0
    for game in games_result:
        if not game.get("name"):
            continue

        images = [GameImageCreate(game_id=1, image=i.get("image")) for i in game.get("short_screenshots")]
        game_data = GameCreate(images=images, **game)
        game_obj = None

        async with uow:
            try:
                game_obj = await uow.games.add(game_data)

                success += 1
                logging.info(f"Game added: {game}")
                await uow.commit()

            except Exception as e:
                logging.error(e)
                await uow.rollback()
                continue

        if game_obj:
            await searcher_torrents(game_obj)

    await redis.setex(name="metadata_page", value=page, time=timedelta(minutes=60))
    logging.info(f"Success added games: {success}")
