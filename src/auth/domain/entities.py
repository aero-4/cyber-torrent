import datetime
import enum

from pydantic import BaseModel


class TokenType(enum.StrEnum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"



class TokenData(BaseModel):
    iat: datetime.datetime | None = None
    exp: datetime.datetime | None = None
    iss: str | None = None
    sub: int | None = None
    jti: str | None = None


class UserCreate(BaseModel):
    email: str
    password: str
