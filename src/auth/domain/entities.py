import datetime
import enum

from pydantic import BaseModel


class TokenType(enum.StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class Tokens(BaseModel):
    access: str
    refresh: str


class TokenData(BaseModel):
    iss: str | None = None
    exp: datetime.datetime | None = None
    payload: dict | None = None


class UserCreate(BaseModel):
    email: str
    password: str


