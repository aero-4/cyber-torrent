import abc

from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.entities import TokenType
from src.users.domain.entities import User
from src.users.infrastructure.db.orm import UsersOrm

import abc

from src.auth.domain.entities import TokenData, TokenType
from src.users.domain.entities import User


class ITokenProvider(abc.ABC):

    @abc.abstractmethod
    def token_read(self, token: str) -> TokenData | None:
        pass

    @abc.abstractmethod
    def create_access_token(self, data: dict, expire: int) -> str:
        pass

    @abc.abstractmethod
    def create_refresh_token(self, data: dict) -> str:
        pass

    @abc.abstractmethod
    async def decode_jwt_without_secret(self, token: str) -> dict:
        pass


class ITokenStorage(abc.ABC):

    @abc.abstractmethod
    async def is_active_token(self, jti: str) -> bool:
        pass

    @abc.abstractmethod
    async def is_valid_token_email(self, email: str, token: str) -> bool:
        pass

    @abc.abstractmethod
    async def add_store_token(self, token_data: TokenData) -> None:
        pass

    @abc.abstractmethod
    async def add_email_token(self, email: str, token: str) -> None:
        pass

    @abc.abstractmethod
    async def remove_tokens_user(self, token_data: TokenData) -> None:
        pass


class ITokenAuth(abc.ABC):

    def __init__(self, response: Response, request: Request):
        self.response = response
        self.request = request

    @abc.abstractmethod
    async def read_token(self, token_type: TokenType) -> TokenData | None:
        pass

    @abc.abstractmethod
    async def set_tokens(self, user: User) -> None:
        pass

    @abc.abstractmethod
    async def set_fast_token(self, user: User, method: str, expire: int) -> None:
        pass

    @abc.abstractmethod
    async def refresh_access_token(self) -> None:
        pass
