from pydantic import BaseModel


class TorrentCreateDTO(BaseModel):
    name: str
    seeders: int
    magnet: str
