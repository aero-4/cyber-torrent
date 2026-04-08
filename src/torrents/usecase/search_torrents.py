from src.torrents.infrastructure.services.torrents_loader import TorrentSearchProvider


async def search_torrents(query: str):
    provider = TorrentSearchProvider()
    return await provider.search(query)

