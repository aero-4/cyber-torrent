from src.auth.domain.entities import UserCreate
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.infrastructure.providers.hasher import HasherProvider
from src.auth.presentation.dtos import UserRegisterDTO
from src.users.infrastructure.db.uow import UsersUnitOfWork


async def registration(user_data: UserRegisterDTO, auth: ITokenAuth) -> None:
    user_data = UserCreate(**user_data.model_dump())

    uow = UsersUnitOfWork()
    hasher_provider = HasherProvider()

    async with uow:
        await uow.users.get_by_email(user_data)

        user_data.password = hasher_provider.hash_password(
            user_data.password
        )

        user = await uow.users.add(user_data)
        await uow.commit()

    return await auth.set_tokens(user)
