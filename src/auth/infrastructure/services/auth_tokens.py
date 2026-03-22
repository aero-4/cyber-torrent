from abc import ABC

from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.entities import TokenType, TokenData, Tokens
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.domain.interfaces.token_provider import ITokenProvider
from src.users.domain.entities import User
from src.users.infrastructure.db.orm import UsersOrm


class TokenAuth(ITokenAuth, ABC):

    def __init__(self, request: Request, provider: ITokenProvider, response: Response = None):
        self.response = response
        self.request = request
        self.provider = provider

    async def read_token(self, token_type: TokenType) -> User | None:
        token = self._get_access_token() if token_type == TokenType.ACCESS else self._get_refresh_token()

        if not token:
            return None

        data = self.provider.decode_token(token)

        return User(
            id=data.get("sub")
        )

    async def set_tokens(self, user: UsersOrm):
        token_data = TokenData(
            payload={"sub": str(user.id)}
        )

        access = self.provider.create_access_token(token_data)
        refresh = self.provider.create_refresh_token(token_data)

        tokens = Tokens(access=access, refresh=refresh)

        if self.response:
            self.set_cookies(tokens)

        self.set_headers(tokens)

        return tokens

    def _get_access_token(self):
        return self.get_cookie("access_token")

    def _get_refresh_token(self):
        return self.get_cookie("refresh_token")

    def get_cookie(self, name: str) -> str:
        return self.request.cookies.get(name)

    def get_header(self, name: str) -> str:
        if header := self.response.headers.get(name):
            return header.split(" ")[-1]


    def set_cookies(self, tokens: Tokens):
        self.response.set_cookie(
            "access_token", tokens.access
        )
        self.response.set_cookie(
            "refresh_token", tokens.refresh
        )

    def set_headers(self, tokens: Tokens):
        self.response.headers["Authorization"] = f"Bearer {tokens.access}"
