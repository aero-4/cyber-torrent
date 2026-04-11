import asyncio
import logging

from src.games.domain.entities import GameCreate
from src.games.infrastructure.db.uow import GamesUnitOfWork
from src.torrents.infrastructure.db.repositories import PGTorrentsRepository
from src.torrents.infrastructure.db.uow import TorrentsUnitOfWork
from src.torrents.infrastructure.services.metadata_loader import MetadataParser
from src.torrents.infrastructure.tasks.torrent import searcher_torrents


async def searcher_games() -> None:
    metadata = MetadataParser()
    uow = GamesUnitOfWork()
    games_result = await metadata.search()
    success = 0
    for game in games_result:
        if not game.get("name"):
            continue

        game_data = GameCreate(**game)
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

        await searcher_torrents(game_obj)

    logging.info(f"Success added games: {success}")
