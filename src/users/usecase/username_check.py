from src.users.infrastructure.db.uow import UsersUnitOfWork
from src.users.presentation.dtos import UsernameDTO


async def check_username(data: UsernameDTO) -> None:
    uow = UsersUnitOfWork()

    async with uow:
        await uow.users.get_by_username(data.username)

    return None