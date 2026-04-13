import abc
from email.message import Message


class IEmailProvider(abc.ABC):

    async def send_confirm_2fa_message(self, email: str):
        pass

    async def sent_confirm_first_email_message(self, email: str):
        pass

    async def send_confirm_message(self, email: str, token: str | int, content_mail: str) -> None:
        pass

    async def send_to_mail(self, mail_message: Message) -> None:
        pass

    def mail_message(self,
                     to_email: str,
                     subject: str = None,
                     content: str = None,
                     from_mail: str = None) -> Message:
        pass

    async def validate_token(self, token: str):
        pass