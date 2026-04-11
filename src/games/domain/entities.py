import datetime

from pydantic import BaseModel

from src.torrents.domain.entities import Torrent


class GameImage(BaseModel):
    id: int
    game_id: int
    image: str


class Game(BaseModel):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    name: str
    slug: str
    genre: str | None
    platform: str | None
    metacritic: int | None
    release_date: datetime.datetime | None
    background_image: str | None
    torrents: list[Torrent] | None = None
    game_images: list[GameImage] | None = None


class GameCreate(BaseModel):
    name: str
    slug: str
    genre: str | None = None
    platform: str | None = None
    metacritic: int | None = None
    release_date: datetime.datetime | None = None
    background_image: str | None = None
    description_raw: str | None = None


class GameImageCreate(BaseModel):
    game_id: int
    image: str
