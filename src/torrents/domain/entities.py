import datetime

from pydantic import BaseModel


class Torrent(BaseModel):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    name: str
    seeders: int
    magnet: str


class TorrentCreate(BaseModel):
    slug: str
    name: str
    seeders: int
    magnet: str
