import datetime
import enum

from pydantic import BaseModel


class UserRoles(enum.IntEnum):
    SUPER_ADMIN = 4
    ADMIN = 3
    MANAGER = 2
    USER = 1
    NOT_VERIFIED = 0


class TokenType(enum.StrEnum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"


class UserVerifications(enum.StrEnum):
    FIRST_CONFIRM_EMAIL = "first-confirm-email"
    TWO_AUTH_EMAIL = "2fa-email"


class TokenData(BaseModel):
    iat: datetime.datetime | None = None
    exp: datetime.datetime | None = None
    iss: str | None = None
    sub: int | None = None
    jti: str | None = None


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_verify_email: bool = False
    avatar_image: str | None = None
    role: UserRoles | None = None


class UserUpdate(BaseModel):
    id: int | None = None
    email: str | None = None
    is_verify_otp: bool | None = None
    is_verify_email: bool | None = None
    avatar_image: str | None = None
    role: UserRoles | None = None
    otp_secret: str | None = None