import datetime
import enum

from pydantic import BaseModel


class TokenType(enum.StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class Tokens(BaseModel):
    access: str | None = None
    refresh: str | None = None


class TokenData(BaseModel):
    iat: datetime.datetime | None = None
    exp: datetime.datetime | None = None
    iss: str | None = None
    sub: int | None = None
    jti: str | None = None
    payload: dict | None = None


class UserCreate(BaseModel):
    email: str
    password: str
