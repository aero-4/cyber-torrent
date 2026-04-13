import logging

from src.auth.domain.entities import UserCreate, UserRoles, UserVerifications
from src.auth.domain.interfaces.email import IEmailProvider
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.infrastructure.providers.hasher import HasherProvider
from src.core.domain.exceptions import BadRequest
from src.users.domain.exceptions import UserAlreadyExists
from src.users.infrastructure.db.uow import UsersUnitOfWork


async def registration(email: str, password: str, auth: ITokenAuth, email_provider: IEmailProvider) -> None:
    user_data = UserCreate(email=email,
                           password=password,
                           role=UserRoles.NOT_VERIFIED)
    uow = UsersUnitOfWork()
    hasher_provider = HasherProvider()

    async with uow:
        if await uow.users.get_by_email(email):
            raise UserAlreadyExists()

        user_data.password = hasher_provider.hash_password(
            user_data.password
        )

        user = await uow.users.add(user_data)
        await uow.commit()

        if not user.is_verify_email:
            await email_provider.sent_confirm_first_email_message(email)
            await auth.set_fast_token(user, method=UserVerifications.FIRST_CONFIRM_EMAIL)

            raise BadRequest(f"Sent code on '{email}'")

    await auth.set_tokens(user)

