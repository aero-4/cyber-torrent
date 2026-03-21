import datetime
import enum

from pydantic import BaseModel


class TokenType(enum.StrEnum):
    access_token = "access"
    refresh_token = "refresh"


class TokenPair(BaseModel):
    access: str
    refresh: str


class TokenData(BaseModel):
    iss: str | None = None
    exp: datetime.datetime | None = None
    type: TokenType | None = None
    user_id: int | None
    payload: dict | None = None


class UserCreate(BaseModel):
    email: str
    password: str
