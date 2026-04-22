import random
import secrets

from src.auth.domain.interfaces.email import IEmailProvider
from src.auth.presentation.dependencies import EmailProvideDep, get_email_provide
from src.core.config import config
from src.core.taskiq_app import broker


email_provider = get_email_provide()

@broker.task
async def send_confirm_2fa_message(email: str) -> None:
    token = secrets.token_urlsafe(32)
    content_mail = config.email.TWO_FACTOR_EMAIL_MESSAGE_TEMPLATE.format(
        link=f"{config.app.APP_URI}/auth/email/confirm/{token}",
        expire_minutes=int(config.email.TWO_FACTOR_TOKEN_EXPIRE_SECONDS / 60)
    )
    return await email_provider.send_confirm_message(email, token, content_mail)


@broker.task
async def sent_2fa_code_email_message(email: str) -> None:
    rand_number = random.randint(100000, 999999)
    content_mail = config.email.CONFIRM_EMAIL_MESSAGE_TEMPLATE.format(
        code=rand_number,
        expire_minutes=int(config.email.CONFIRM_CODE_EMAIL_EXPIRE_SECONDS / 60)
    )
    return await email_provider.send_confirm_message(email, rand_number, content_mail)
