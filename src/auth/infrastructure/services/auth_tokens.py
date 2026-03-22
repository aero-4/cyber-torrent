from abc import ABC

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.entities import TokenType, TokenData, Tokens
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.domain.interfaces.token_provider import ITokenProvider
from src.core.config import config
from src.users.domain.entities import User
from src.users.infrastructure.db.orm import UsersOrm


class TokenAuth(ITokenAuth, ABC):
    """
    Create authorization tokens and read
    """

    def __init__(self, request: Request, provider: ITokenProvider, response: Response = None):
        self.response = response
        self.request = request
        self.token_provider = provider

    async def read_token(self, token_type: TokenType) -> User | None:
        token: str = self._get_access_token() if token_type == TokenType.ACCESS else self._get_refresh_token()
        token_data: TokenData = self.token_provider.read_token(token)

        if not token_data:
            return None

        return User(
            id=token_data.sub
        )

    async def inject_access(self, response: Response):
        if hasattr(self.request.state, "access_token"):
            access_token = self.request.state.access_token
            self.response = response

            await self.set_token(access_token)

    async def set_token(self, token: str):
        tokens = Tokens(access=token)

        self.set_cookies(tokens)
        self.set_headers(tokens)

    async def refresh_access_token(self):
        refresh_data_user: User = await self.read_token(TokenType.REFRESH)

        if not refresh_data_user:
            raise Exception(
                "Not valid refresh token"
            )

        token_data = {"sub": str(refresh_data_user.id)}
        access_token = self.token_provider.create_access_token(token_data)

        self.request.state.access_token = access_token

        tokens = Tokens(access=access_token)

        self.set_headers(tokens)
        self.set_cookies(tokens)

        return access_token

    async def set_tokens(self, user: User):
        token_data = {"sub": str(user.id)}

        access = self.token_provider.create_access_token(token_data)
        refresh = self.token_provider.create_refresh_token(token_data)

        tokens = Tokens(access=access, refresh=refresh)

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
        if self.response:
            self.response.set_cookie(
                key="access_token",
                value=tokens.access,
            )
            if tokens.refresh:
                self.response.set_cookie(
                    key="refresh_token",
                    value=tokens.refresh
                )

    def set_headers(self, tokens: Tokens):
        if self.response:
            self.response.headers["Authorization"] = f"Bearer {tokens.access}"
            if tokens.refresh:
                self.response.headers["X-Refresh-Token"] = f"Bearer {tokens.refresh}"
