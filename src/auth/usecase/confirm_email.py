import secrets

from src.auth.domain.entities import UserUpdate
from src.auth.domain.interfaces.email import IEmailProvider
from src.core.config import config
from src.users.infrastructure.db.uow import UsersUnitOfWork


async def email_send_token(email: str, email_provider: IEmailProvider):
    token = secrets.token_urlsafe(32)
    content_mail = config.email.TWO_FACTOR_EMAIL_MESSAGE_TEMPLATE.format(
        link=f"{config.app.APP_URI}/auth/email/confirm/{token}"
    )
    msg = email_provider.mail_message(email, content=content_mail)
    await email_provider.send_to_mail(msg)
    await email_provider.storage.add_email_token(email, token)


async def confirm_email_user(token: str, email_provider: IEmailProvider):
    uow = UsersUnitOfWork()

    async with uow:
        email = await email_provider.validate_token(token)
        user_data = UserUpdate(email=email, is_verify_email=True)

        await uow.users.update(user_data)
        await uow.commit()
