from taskiq.middlewares.taskiq_admin_middleware import TaskiqAdminMiddleware
from taskiq_aio_pika.broker import AioPikaBroker
from src.core.config import config

broker = AioPikaBroker(config.taskiq.RABBITMQ_URL)
