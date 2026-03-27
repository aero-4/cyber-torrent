import logging

from src.auth.domain.entities import UserCreate
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.infrastructure.providers.hasher import HasherProvider
from src.users.domain.exceptions import UserAlreadyExists
from src.users.infrastructure.db.uow import UsersUnitOfWork


async def registration(email: str, password: str, auth: ITokenAuth) -> None:
    user_data = UserCreate(email=email, password=password)
    uow = UsersUnitOfWork()
    hasher_provider = HasherProvider()

    async with uow:
        if await uow.users.get_by_email(email):
            raise UserAlreadyExists()

        user_data.password = hasher_provider.hash_password(
            user_data.password
        )

        user = await uow.users.add(user_data)
        await auth.set_tokens(user)

        await uow.commit()
