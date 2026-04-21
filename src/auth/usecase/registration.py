import asyncio
import logging

from src.auth.domain.entities import UserCreate, UserRoles, UserVerifications
from src.auth.domain.interfaces.email import IEmailProvider
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.infrastructure.providers.hasher import HasherProvider
from src.auth.presentation.dtos import UserRegisterDTO
from src.core.config import config
from src.users.domain.exceptions import UserAlreadyExists
from src.users.infrastructure.db.uow import UsersUnitOfWork
from src.auth.infrastructure.tasks.confirm_message import sent_2fa_code_email_message


async def registration(user_data: UserRegisterDTO, auth: ITokenAuth, email_provider: IEmailProvider) -> str:
    user_data = UserCreate(role=UserRoles.NOT_VERIFIED, **user_data.model_dump())
    uow = UsersUnitOfWork()
    hasher_provider = HasherProvider()

    async with uow:
        if await uow.users.get_by_email(user_data.email):
            raise UserAlreadyExists()

        user_data.password = hasher_provider.hash_password(
            user_data.password
        )

        user = await uow.users.add(user_data)
        await uow.commit()

        if not user.is_verify_email:
            await sent_2fa_code_email_message.kiq(user_data.email)
            # asyncio.create_task(sent_2fa_code_email_message(email_provider, user_data.email))
            await auth.set_fast_token(user,
                                      method=UserVerifications.FIRST_CONFIRM_EMAIL,
                                      expire=config.email.TWO_FACTOR_TOKEN_EXPIRE_SECONDS)
            return "confirm_email"

    await auth.set_tokens(user)
