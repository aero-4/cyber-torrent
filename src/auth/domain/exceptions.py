from src.core.domain.entities import ERROR_CODES
from src.core.domain.exceptions import AppException, BadRequest


class AuthRequired(AppException):
    message = "Authentication required"
    status_code = 401
    error_code = ERROR_CODES.get(status_code)


class NotValidEmailPassword(BadRequest):
    message = "Not valid password or email"


class RefreshInvalid(AuthRequired):
    message = "Refresh token invalid"


class OTPRequired(AuthRequired):
    message = "OTP code required"


class OTPInputRequired(AuthRequired):
    message = "Not input OTP code"


class OTPInvalid(AuthRequired):
    message = "OTP code is invalid"
