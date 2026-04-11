import datetime

from pydantic import BaseModel


class Torrent(BaseModel):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    name: str
    seeders: int
    magnet: str
    size: int | None = None


class TorrentCreate(BaseModel):
    name: str
    seeders: int
    magnet: str
    size: int
    game_id: int


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


class GameCreate(BaseModel):
    name: str
    slug: str
    genre: str
    platform: str
    metacritic: int
    release_date: datetime.datetime
    background_image: str


