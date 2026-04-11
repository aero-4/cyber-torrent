from sqlalchemy import Text

from src.games.domain.entities import GameImage, Game
from src.torrents.infrastructure.db.orm import *
from src.utils.datetimes import get_timezone_now


class GamesImages(Base):
    __tablename__ = "game_images"

    game: Mapped["GamesOrm"] = relationship(back_populates="game_images")
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"))
    image: Mapped[str] = mapped_column(String(), nullable=False)

    def to_entity(self):
        return GameImage(
            id=self.id,
            game_id=self.game_id,
            image=self.image
        )


class GamesOrm(Base):
    __tablename__ = "games"

    name: Mapped[str] = mapped_column(String(), nullable=False)
    slug: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    genre: Mapped[str] = mapped_column(String(), nullable=True)
    platform: Mapped[str] = mapped_column(String(), nullable=True)
    metacritic: Mapped[int] = mapped_column(Integer(), nullable=True)
    release_date: Mapped[datetime.datetime] = mapped_column(DateTime(), default=get_timezone_now, nullable=True)
    background_image: Mapped[str] = mapped_column(String(), nullable=True)
    description_raw: Mapped[str] = mapped_column(Text(), nullable=True)
    torrents: Mapped[List["TorrentsOrm"]] = relationship(back_populates="game_torrent", uselist=True)
    game_images: Mapped[List["GamesImages"]] = relationship(back_populates="game")

    def to_entity(self):
        return Game(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            name=self.name,
            slug=self.slug,
            genre=self.genre,
            platform=self.platform,
            metacritic=self.metacritic,
            release_date=self.release_date,
            background_image=self.background_image
        )
