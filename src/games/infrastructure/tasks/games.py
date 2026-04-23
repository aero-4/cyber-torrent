import asyncio
import logging
from datetime import timedelta

from src.core.infrastructure.redis import get_redis_client
from src.games.domain.entities import GameCreate, GameTagsCreate
from src.games.infrastructure.db.uow import GamesUnitOfWork
from src.torrents.infrastructure.services.metadata_loader import MetadataParser
from src.torrents.infrastructure.tasks.torrent import searcher_torrents


async def searcher_nullable_torrents():
    uow = GamesUnitOfWork()

    logging.info("Check nullable magnet-links games...")

    async with uow:
        games = await uow.games.get_without_torrents()
        logging.info("Games count %s", len(games))

    for game in games:
        await searcher_torrents(game)

    logging.info("Checker nullable magnet-links finished!")
