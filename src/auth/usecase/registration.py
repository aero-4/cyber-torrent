import logging

from fastapi import HTTPException

from src.auth.domain.entities import UserCreate
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.infrastructure.providers.hasher import HasherProvider
from src.core.domain.exceptions import AppException
from src.users.infrastructure.db.uow import UsersUnitOfWork


async def registration(email: str, password: str, auth: ITokenAuth) -> None:
    user_data = UserCreate(email=email, password=password)

    uow = UsersUnitOfWork()
    hasher_provider = HasherProvider()

    async with uow:
        logging.info("Creating user")

        if await uow.users.get_by_email(email):
            logging.error("User already exists with email=%s", email)
            raise AppException(message="Email already exists",
                               status_code=404)

        user_data.password = hasher_provider.hash_password(
            user_data.password
        )

        user = await uow.users.add(user_data)
        await uow.commit()

        logging.info("Created user=%s", (user,))
    return await auth.set_tokens(user)
