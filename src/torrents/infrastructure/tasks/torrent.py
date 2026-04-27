import logging

from src.core.domain.exceptions import AlreadyExists
from src.torrents.domain.entities import TorrentCreate, Game
from src.torrents.infrastructure.db.uow import TorrentsUnitOfWork
from src.torrents.infrastructure.services.torrents_loader import TorrentSearchProvider


async def searcher_torrents(game: Game) -> None:
    torrent = TorrentSearchProvider()
    uow = TorrentsUnitOfWork()
    success = 0

    logging.info("Game: %s | Finding magnet-links...", game.name)

    search_results = await torrent.search(game.name)
    if not search_results:
        logging.info("No find magnet-links")
        return None

    async with uow:
        for torrent_data in search_results:
            t_data = TorrentCreate(game_id=game.id, **torrent_data)
            try:
                await uow.torrents.add(t_data)
                await uow.commit()

                success += 1
                logging.info(f"Added torrent: %s", t_data.name)
            except AlreadyExists as e:
                logging.error(f'Error adding torrent: %s', e)

    logging.info(f"Success magnet-links added: %s", success)
