from taskiq.middlewares.taskiq_admin_middleware import TaskiqAdminMiddleware
from taskiq_aio_pika.broker import AioPikaBroker
from src.core.config import config
from src.auth.infrastructure.tasks.confirm_message import *

broker = AioPikaBroker(config.taskiq.RABBITMQ_URL)
# .with_result_backend(config.taskiq.RABBITMQ_BACKEND_RESULT)
# .with_middlewares(
#     TaskiqAdminMiddleware(
#         url="http://localhost:8888",
#         api_token="supersecret",
#         taskiq_broker_name="my_worker",
#     )
# )
