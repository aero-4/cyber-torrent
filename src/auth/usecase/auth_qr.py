from fastapi import HTTPException

from src.auth.domain.entities import UserUpdate
from src.auth.domain.exceptions import NotValidEmailPassword
from src.auth.infrastructure.providers.qr import QrCodeProvider
from src.users.infrastructure.db.uow import UsersUnitOfWork

qr_provider = QrCodeProvider()


async def generate_qr_code(user_email: str) -> bytes:
    qr_data = qr_provider.create_qr_code(user_email)
    return qr_data


async def authenticate_opt_code(code: str, email: str):
    uow = UsersUnitOfWork()
    async with uow:
        if not qr_provider.check_otp_code(code=code):
            raise HTTPException(
                status_code=404,
                detail="OTP code is invalid"
            )

        data = UserUpdate(
            email=email,
            is_verify_otp=True
        )

        if not await uow.users.get_by_email(email=email):
            raise NotValidEmailPassword()

        await uow.users.update(data)



