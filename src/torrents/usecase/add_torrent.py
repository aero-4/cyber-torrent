from slugify import slugify

from src.torrents.domain.entities import TorrentCreate, Torrent
from src.torrents.infrastructure.db.uow import TorrentsUnitOfWork
from src.torrents.presentation.dtos import TorrentCreateDTO


async def add_torrent(dto: TorrentCreateDTO) -> Torrent:
    uow = TorrentsUnitOfWork()
    t_data = TorrentCreate(slug=slugify(dto.name), **dto.model_dump())

    async with uow:
        torrent = await uow.torrents.add(t_data)
        await uow.commit()

    return torrent
