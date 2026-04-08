from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.domain.exceptions import AlreadyExists, NotFound
from src.torrents.domain.entities import TorrentCreate, Torrent
from src.torrents.infrastructure.db.orm import TorrentsOrm


class PGTorrentsRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, t_data: TorrentCreate) -> Torrent:
        obj = TorrentsOrm(**t_data.model_dump())
        try:
            self.session.add(obj)
            await self.session.flush()
        except IntegrityError:
            raise AlreadyExists(message=f"Torrent '{t_data.name}' already exists")

        return obj.to_entity()

    async def get_all(self) -> list[Torrent]:
        stmt = (
            select(TorrentsOrm)
            .order_by(
                func.desc(TorrentsOrm.created_at)
            ))
        results = await self.session.execute(stmt)
        results = results.unique().scalars().all()

        return [i.to_entity() for i in results]

    async def get_one(self, slug: str):
        stmt = (
            select(TorrentsOrm.slug == slug)
        )
        result = await self.session.execute(stmt)
        obj: Torrent | None = result.scalar_one_or_none()

        if not obj:
            raise NotFound(message=f"Torrent '{slug}' not found")

        return obj.to_entity()

    async def update(self):
        pass

    async def get_by_filters(self):
        pass
