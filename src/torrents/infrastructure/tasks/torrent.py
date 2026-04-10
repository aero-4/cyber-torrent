import asyncio
import datetime
import random

import celery
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# from src.core.celery_app import celery_app
from src.torrents.infrastructure.db.uow import TorrentsUnitOfWork
from src.torrents.infrastructure.services.metadata_loader import MetadataParser
from src.torrents.infrastructure.services.torrents_loader import TorrentSearchProvider


# Выносим всю асинхронную логику в отдельную корутину
async def _run_search_and_save():
    torrent = TorrentSearchProvider()
    uow = TorrentsUnitOfWork()

    # Просто ждем завершения поиска с помощью await
    search_results = await torrent.search("god of war")
    print(f"Найдено торрентов: {len(search_results)}")

    async with uow:
        for torrent_data in search_results:
            torr = await uow.torrents.add(torrent_data)
            print(torr)
        await uow.commit()

    return "Успешно сохранено"


# # Сама таска Celery остается СИНХРОННОЙ (def, а не async def)
# @celery_app.task(bind=True)
# def search_games_task(self):
#     # Запускаем асинхронный цикл событий
#     result = asyncio.run(_run_search_and_save())
#     return result


def setup_tasks(scheduler: AsyncIOScheduler):
    scheduler.add_job(_run_search_and_save, "interval", minutes=10, next_run_time=datetime.datetime.now())

    scheduler.start()