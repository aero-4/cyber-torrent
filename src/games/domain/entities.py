import datetime

from pydantic import BaseModel

from src.torrents.domain.entities import Torrent


class GameImage(BaseModel):
    id: int
    game_id: int
    image: str


class GameTag(BaseModel):
    game_id: int
    image: str
    name: str


class Game(BaseModel):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    name: str
    slug: str
    description_raw: str | None = None
    genre: str | None
    platform: str | None
    metacritic: int | None
    release_date: datetime.datetime | None
    background_image: str | None
    torrents: list[Torrent] | None = None
    game_images: list[GameImage] | None = None
    tags: list[GameTag] | None = None
    similar: list | None = None


class GameImageCreate(BaseModel):
    image: str


class GameTagsCreate(BaseModel):
    name: str
    image: str


class GameCreate(BaseModel):
    name: str
    slug: str
    genre: str | None = None
    platform: str | None = None
    metacritic: int | None = None
    release_date: datetime.datetime | None = None
    background_image: str | None = None
    description_raw: str | None = None
    images: list[str] | None = None
    tags: list[GameTagsCreate] | None = None
