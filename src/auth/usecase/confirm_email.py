from starlette.requests import Request

from src.auth.domain.entities import UserUpdate, UserRoles
from src.auth.domain.interfaces.email import IEmailProvider
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.users.domain.entities import User
from src.users.infrastructure.db.uow import UsersUnitOfWork


async def confirm_email(user: User, token: str | int, email_provider: IEmailProvider, auth: ITokenAuth):
    uow = UsersUnitOfWork()

    async with uow:
        email = await email_provider.validate_token(user.email, token)
        user_data = UserUpdate(email=email,
                               is_verify_email=True,
                               role=UserRoles.USER)

        user = await uow.users.update(user_data)
        await uow.commit()

    await auth.set_tokens(user)


