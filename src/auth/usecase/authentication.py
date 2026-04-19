from src.auth.domain.exceptions import NotValidCredentials, OTPRequired, OTPInvalid, EmailCodeRequired
from src.auth.domain.interfaces.email import IEmailProvider
from src.auth.domain.interfaces.hasher import IHasherProvider
from src.auth.domain.interfaces.qrcode import IQrCodeProvider
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.presentation.dtos import UserLoginDTO
from src.users.infrastructure.db.uow import UsersUnitOfWork
from src.auth.infrastructure.tasks.confirm_message import sent_2fa_code_email_message


async def authenticate(login_data: UserLoginDTO,
                       auth: ITokenAuth,
                       hasher_provider: IHasherProvider,
                       qr_code_provider: IQrCodeProvider) -> None:
    uow = UsersUnitOfWork()

    async with uow:
        user = await uow.users.get_by_email(login_data.email)

        if not user or not hasher_provider.verify_password(login_data.password, user.password):
            raise NotValidCredentials(details=login_data.model_dump())

        if user.is_verify_otp and not login_data.otp_code:
            raise OTPRequired(details=login_data.model_dump())

        if user.is_verify_otp and login_data.otp_code and not qr_code_provider.check_otp_code(code=login_data.otp_code, secret=user.otp_secret):
            raise OTPInvalid(details=login_data.model_dump())

        if user.is_verify_email and not login_data.email_code:
            await sent_2fa_code_email_message.kiq(login_data.email)
            raise EmailCodeRequired()


    await auth.set_tokens(user)
