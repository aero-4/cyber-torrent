from src.auth.domain.entities import UserUpdate
from src.auth.domain.interfaces.hasher import IHasherProvider
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.core.domain.exceptions import BadRequest
from src.users.domain.entities import User
from src.users.infrastructure.db.uow import UsersUnitOfWork
from src.users.presentation.dtos import ChangePasswordDTO


async def change_password_user(user: User, password: ChangePasswordDTO, hasher: IHasherProvider, auth: ITokenAuth):
    uow = UsersUnitOfWork()
    user_data = UserUpdate(email=user.email,
                           password=hasher.hash_password(password.new_password))
    async with uow:
        if not hasher.verify_password(password.old_password, user.password):
            raise BadRequest("Not valid password")

        await uow.users.update(user_data)
        await uow.commit()

    await auth.set_tokens(user)
