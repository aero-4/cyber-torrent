import datetime

from pydantic import BaseModel

from src.games.infrastructure.db.orm import GamesImages
from src.torrents.domain.entities import Torrent


class Game(BaseModel):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    name: str
    slug: str
    genre: str
    platform: str
    metacritic: int
    release_date: datetime.datetime
    background_image: str
    torrents: list[Torrent] | None = None
    game_images: list[GamesImages] | None = None


class GameCreate(BaseModel):
    name: str
    slug: str
    genre: str
    platform: str
    metacritic: int
    release_date: datetime.datetime
    background_image: str
