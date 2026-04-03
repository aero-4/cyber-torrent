import secrets

from src.auth.domain.exceptions import NotValidEmailPassword, OTPRequired, OTPInvalid, OTPInputRequired
from src.auth.infrastructure.providers.hasher import HasherProvider
from src.auth.infrastructure.providers.qr import QrCodeProvider
from src.auth.presentation.dependencies import TokenAuthDep
from src.auth.presentation.dtos import UserLoginDTO
from src.users.infrastructure.db.uow import UsersUnitOfWork


async def authenticate(login_data: UserLoginDTO, auth: TokenAuthDep):
    uow = UsersUnitOfWork()
    hasher_provider = HasherProvider()
    qr_provider = QrCodeProvider()

    async with uow:
        user = await uow.users.get_by_email(login_data.email)

        if not user or not hasher_provider.verify_password(login_data.password, user.password):
            raise NotValidEmailPassword()

        if not user.is_verify_otp:
            raise OTPRequired()
        else:
            if user.is_verify_otp and not login_data.otp_code:
                raise OTPInputRequired()

            if login_data.otp_code and not qr_provider.check_otp_code(code=login_data.otp_code):
                raise OTPInvalid()

        await auth.set_tokens(user)
