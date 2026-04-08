from src.db.base import Base
from sqlalchemy import Integer, String, Enum, Boolean
from sqlalchemy.orm import mapped_column, Mapped

from src.torrents.domain.entities import TorrentCreate, Torrent


class TorrentsOrm(Base):
    __tablename__ = "torrents"

    slug: Mapped[str] = mapped_column(String(), nullable=True)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    seeders: Mapped[int] = mapped_column(Integer(), default=0)
    magnet: Mapped[str] = mapped_column(String(length=300), nullable=False)

    def to_entity(self):
        return Torrent(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            name=self.name,
            seeders=self.seeders,
            magnet=self.magnet
        )

