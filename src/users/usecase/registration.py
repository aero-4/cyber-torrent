from src.users.domain.entities import UserCreate
from src.users.domain.interfaces.token_auth import ITokenAuth
from src.users.infrastructure.db.uow import UsersUnitOfWork
from src.users.presentation.dtos import UserRegisterDTO


async def registration(user_data: UserRegisterDTO, auth: ITokenAuth) -> None:
    user_data = UserCreate(**user_data.model_dump())
    uow = UsersUnitOfWork()

    async with uow:
        await uow.users.get_by_email(user_data.email)
        user = await uow.users.add()
        await uow.commit()

        await auth.set_tokens(user.id)

