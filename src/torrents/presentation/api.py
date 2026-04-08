from fastapi import APIRouter

from src.torrents.infrastructure.services.torrents_loader import TorrentSearchProvider
from src.torrents.presentation.dtos import TorrentCreateDTO
from src.torrents.usecase.add_torrent import add_torrent
from src.torrents.usecase.collect_torrents import collect_torrents, collect_torrent
from src.torrents.usecase.search_torrents import search_torrents

router = APIRouter()


@router.post("/")
async def create_torrent(torrent_data: TorrentCreateDTO):
    return await add_torrent(torrent_data)


@router.get("/")
async def get_all_torrents():
    return await collect_torrents()


@router.get("/{slug}")
async def get_torrent(slug: str):
    return await collect_torrent(slug)


@router.get("/search")
async def search(query: str):
    return await search_torrents(query)