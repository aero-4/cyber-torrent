from fastapi import HTTPException

from src.auth.domain.entities import UserUpdate
from src.auth.domain.exceptions import OTPInvalid, NotValidCredentials
from src.auth.infrastructure.providers.qr import QrCodeProvider
from src.users.infrastructure.db.uow import UsersUnitOfWork

qr_provider = QrCodeProvider()


def generate_qr_code(user_email: str) -> str:
    qr_file_name = qr_provider.create_qr_code(user_email)
    return qr_file_name


async def authenticate_opt_code(code: str, email: str):
    uow = UsersUnitOfWork()
    data = UserUpdate(
        email=email,
        is_verify_otp=True
    )

    async with uow:
        user = await uow.users.get_by_email(email=email)

        if not user:
            raise NotValidCredentials()

        if not qr_provider.check_otp_code(code=code):
            raise OTPInvalid()

        if not user.is_verify_otp:
            await uow.users.update(data)
            await uow.commit()
