from src.torrents.domain.entities import Torrent
from src.torrents.infrastructure.db.uow import TorrentsUnitOfWork


async def collect_torrents():
    uow = TorrentsUnitOfWork()

    async with uow:
        return await uow.torrents.get_all()


async def collect_torrent(slug: str) -> Torrent:
    uow = TorrentsUnitOfWork()

    async with uow:
        return await uow.torrents.get_one(slug)
