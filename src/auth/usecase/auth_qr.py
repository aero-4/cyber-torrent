import pyotp
from fastapi import HTTPException

from src.auth.domain.entities import UserUpdate
from src.auth.domain.exceptions import OTPInvalid, NotValidCredentials
from src.auth.domain.interfaces.token_auth import ITokenProvider, ITokenAuth
from src.auth.infrastructure.providers.qr import QrCodeProvider
from src.core.domain.exceptions import NotFound
from src.users.domain.entities import User
from src.users.infrastructure.db.uow import UsersUnitOfWork

qr_provider = QrCodeProvider()


async def generate_qr_code(user: User) -> str:
    uow = UsersUnitOfWork()
    otp_secret = user.otp_secret

    if not user.otp_secret:
        async with uow:
            otp_secret = pyotp.random_base32()
            user_data = UserUpdate(
                email=user.email,
                otp_secret=otp_secret
            )
            await uow.users.update(user_data)
            await uow.commit()

    qr_file_name = qr_provider.create_qr_code(user.email, otp_secret)
    return qr_file_name


async def authenticate_opt_code(code: str, user: User, auth: ITokenAuth):
    uow = UsersUnitOfWork()
    async with uow:
        user = await uow.users.get_by_id(user.id)
        if not qr_provider.check_otp_code(code=code, secret=user.otp_secret):
            raise OTPInvalid()

        await uow.users.update(
            UserUpdate(is_verify_otp=True,
                       email=user.email)
        )
        await uow.commit()

        await auth.set_tokens(user)
