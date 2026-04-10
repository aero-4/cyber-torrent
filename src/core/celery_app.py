from celery import Celery
from src.core.config import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# celery_app = Celery("src.core",
#                     broker=config.celery.CELERY_BROKER_URL,
#                     backend=config.celery.CELERY_RESULT_BACKEND,
#                     include=["src.torrents.infrastructure.tasks",])
#
# celery_app.conf.beat_schedule = {
#     "scrape_magnet_links": {
#         "task": "src.torrents.infrastructure.tasks.torrent.scrape_magnet_links",
#         "schedule": 60.0
#     }
# }

