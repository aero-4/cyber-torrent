from taskiq.middlewares.taskiq_admin_middleware import TaskiqAdminMiddleware
from taskiq_aio_pika.broker import AioPikaBroker

from src.core.config import config

broker = (
    AioPikaBroker(config.taskiq.RABBITMQ_URL)
    .with_result_backend(config.taskiq.RABBITMQ_BACKEND_RESULT)
    .with_middlewares(
        TaskiqAdminMiddleware(
            url="http://localhost:8888",  # the url to your taskiq-dashboard instance
            api_token="supersecret",  # secret for accessing the dashboard API
            taskiq_broker_name="my_worker",  # it will be worker name in the dashboard
        )
    )
)
