import asyncio

from src.core.celery_app import celery_app
from src.torrents.infrastructure.db.repositories import PGTorrentsRepository
from src.torrents.infrastructure.db.uow import TorrentsUnitOfWork
from src.torrents.infrastructure.services.metadata_loader import MetadataParser


@celery_app.task(bind=True)
async def search_games_task():
    metadata = MetadataParser()
    uow = TorrentsUnitOfWork()
    result = asyncio.create_task(metadata.search())
    print(result.result())
    async with uow:
        for torrent_data in result:
            torr = await uow.torrents.add(torrent_data)
            print(torr)
        await uow.commit()
