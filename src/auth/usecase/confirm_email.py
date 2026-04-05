from src.auth.domain.entities import UserUpdate
from src.auth.domain.interfaces.email import IEmailProvider
from src.users.infrastructure.db.uow import UsersUnitOfWork


async def email_send_token(email: str, email_provider: IEmailProvider):
    return await email_provider.send_confirm_message(email)


async def confirm_email(token: str, email_provider: IEmailProvider):
    uow = UsersUnitOfWork()

    async with uow:
        email = await email_provider.validate_token(token)
        user_data = UserUpdate(email=email, is_verify_email=True)

        await uow.users.update(user_data)
        await uow.commit()
