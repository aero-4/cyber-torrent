import logging

from src.core.domain.exceptions import AlreadyExists
from src.torrents.domain.entities import TorrentCreate, Game
from src.torrents.infrastructure.db.uow import TorrentsUnitOfWork
from src.torrents.infrastructure.services.torrents_loader import TorrentSearchProvider



async def searcher_torrents(game: Game) -> None:
    logging.info("Loading torrents...")

    query = f"{game.name} repack"
    torrent = TorrentSearchProvider()
    uow = TorrentsUnitOfWork()

    success = 0

    search_results = await torrent.search(query)

    logging.info(f"Search query: {query} | Found torrents: {len(search_results)}")

    async with uow:
        for torrent_data in search_results:
            t_data = TorrentCreate(game_id=game.id, **torrent_data)
            try:
                torr = await uow.torrents.add(t_data)
                success += 1

                logging.info(f"Added torrent: {torr.name}")
                await uow.commit()
            except AlreadyExists as e:
                logging.error(e)

    logging.info(f"Success torrents added: {success}")
