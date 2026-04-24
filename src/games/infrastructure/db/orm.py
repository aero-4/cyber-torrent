from sqlalchemy import Text

from src.core.infrastructure.admin import BaseAdmin
from src.games.domain.entities import GameImage, Game, GameTag
from src.torrents.infrastructure.db.orm import *
from src.utils.admin import format_photo
from src.utils.datetimes import get_timezone_now


class GamesTagsOrm(Base):
    __tablename__ = "game_tags"

    game: Mapped["GamesOrm"] = relationship(back_populates="tags", lazy="joined")
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(), nullable=False)
    image: Mapped[str] = mapped_column(String(), nullable=True)

    def to_entity(self):
        return GameTag(
            game_id=self.game_id,
            image=self.image,
            name=self.name,
        )


class GamesImagesOrm(Base):
    __tablename__ = "game_images"

    game: Mapped["GamesOrm"] = relationship(back_populates="game_images")
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"))
    image: Mapped[str] = mapped_column(String(), nullable=False, unique=True)

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
    torrents: Mapped[List["TorrentsOrm"]] = relationship(back_populates="game_torrent", uselist=True, lazy="select")
    tags: Mapped[List["GamesTagsOrm"]] = relationship(back_populates="game", uselist=True)
    game_images: Mapped[List["GamesImagesOrm"]] = relationship(back_populates="game", uselist=True)

    def to_entity(self, similar=None):
        try:
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
                background_image=self.background_image,
                description_raw=self.description_raw,
                game_images=[i.to_entity() for i in self.game_images],
                torrents=[i.to_entity() for i in self.torrents],
                tags=[i.to_entity() for i in self.tags],
                similar=similar
            )
        except:
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
                background_image=self.background_image,
                description_raw=self.description_raw,
            )


class GamesAdmin(BaseAdmin, model=GamesOrm):
    column_list = [
        GamesOrm.id,
        GamesOrm.name,
        GamesOrm.slug,
        GamesOrm.genre,
        GamesOrm.platform,
        GamesOrm.metacritic,
        GamesOrm.release_date,
        GamesOrm.background_image,
        GamesOrm.description_raw,
    ]

    column_formatters = {
        GamesOrm.background_image: format_photo
    }

    column_formatters_detail = {
        GamesOrm.background_image: lambda m, a: format_photo(m, a, width=250)
    }
