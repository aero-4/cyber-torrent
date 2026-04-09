import datetime
from typing import List

from src.db.base import Base
from sqlalchemy import Integer, String, Enum, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.torrents.domain.entities import TorrentCreate, Torrent, Game, GameImage
from src.utils.datetimes import get_timezone_now





class TorrentsOrm(Base):
    __tablename__ = "torrents"

    name: Mapped[str] = mapped_column(String(), nullable=False)
    seeders: Mapped[int] = mapped_column(Integer(), default=0)
    magnet: Mapped[str] = mapped_column(String(length=300), nullable=False)
    game_torrent: Mapped["GamesOrm"] = relationship(back_populates="torrents", uselist=False)

    def to_entity(self):
        return Torrent(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            name=self.name,
            seeders=self.seeders,
            magnet=self.magnet
        )



