import secrets

from src.auth.domain.exceptions import NotValidEmailPassword
from src.auth.infrastructure.providers.hasher import HasherProvider
from src.auth.infrastructure.providers.qr import QrCodeProvider
from src.auth.presentation.dependencies import TokenAuthDep
from src.auth.presentation.dtos import UserLoginDTO
from src.users.infrastructure.db.uow import UsersUnitOfWork


async def authenticate(login_data: UserLoginDTO, auth: TokenAuthDep):
    uow = UsersUnitOfWork()
    hasher_provider = HasherProvider()

    async with uow:
        user = await uow.users.get_by_email(login_data.email)

        if not user or not hasher_provider.verify_password(login_data.password, user.password):
            raise NotValidEmailPassword()

        await auth.set_tokens(user)


async def generate_qr_code() -> bytes:
    qr_provider = QrCodeProvider()

    qr_data = qr_provider.create_qr_code()
    return qr_data


async def authenticate_with_qr(token: str):
    pass
