import logging
import secrets

import aiosmtplib

from email.message import Message, EmailMessage

from src.auth.domain.exceptions import InvalidTokenEmail, InvalidSentTokenEmail
from src.auth.domain.interfaces.email import IEmailProvider
from src.auth.domain.interfaces.token_auth import ITokenStorage
from src.core.config import config


class SmtpProvider(IEmailProvider):

    def __init__(self,
                 storage: ITokenStorage):
        self.storage = storage

    async def send_confirm_message(self, email: str) -> None:
        token = secrets.token_urlsafe(32)
        content_mail = config.email.TWO_FACTOR_EMAIL_MESSAGE_TEMPLATE.format(
            link=f"{config.app.APP_URI}/auth/email/confirm/{token}"
        )
        msg = self.mail_message(email, content=content_mail)

        await self.send_to_mail(msg)
        await self.storage.add_email_token(email, token)

    async def validate_token(self, token: str) -> str:
        email = await self.storage.is_valid_token_email(token)
        if not email:
            raise InvalidTokenEmail()
        return email

    async def send_to_mail(self, mail_message: Message, timeout: int = 60) -> None:
        try:
            await aiosmtplib.send(
                mail_message,
                hostname=config.email.HOST,
                port=config.email.PORT,
                sender=config.email.EMAIL_USERNAME,
                username=config.email.EMAIL_USERNAME,
                password=config.email.PASSWORD,
                use_tls=config.email.USE_TLS,
                timeout=timeout,
                tls_context=None,
            )
        except Exception as e:
            logging.error(e)
            raise InvalidSentTokenEmail(details={k: v for k, v in mail_message.items()})

    def mail_message(self,
                     to_email: str,
                     subject: str = config.email.TWO_FACTOR_EMAIL_MESSAGE_SUBJECT,
                     content: str = config.email.TWO_FACTOR_EMAIL_MESSAGE_TEMPLATE,
                     from_mail: str = config.email.EMAIL_USERNAME) -> Message:
        message = EmailMessage()

        message["From"] = from_mail
        message["To"] = to_email
        message["Subject"] = subject

        message.set_content(content)

        return message
