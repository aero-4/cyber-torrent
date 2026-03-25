from abc import ABC

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.entities import TokenType, TokenData, Tokens
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.domain.interfaces.token_provider import ITokenProvider
from src.auth.domain.interfaces.transport import IAuthTransport
from src.auth.infrastructure.providers.redis_storage import RedisTokenStorage
from src.users.domain.entities import User


class TokenAuth(ITokenAuth, ABC):
    """
    Create authorization tokens and read
    """

    def __init__(self,
                 request: Request,
                 provider: ITokenProvider,
                 token_storage: RedisTokenStorage,
                 transports: dict[TokenType, list[IAuthTransport]],
                 response: Response = None):
        self.response = response
        self.request = request
        self.token_provider = provider
        self.token_storage = token_storage
        self.transports = transports

    async def read_token(self, token_type: TokenType) -> TokenData | None:
        token: str = self._get_access_token() if token_type == TokenType.ACCESS else self._get_refresh_token()
        token_data: TokenData = self.token_provider.token_read(token)
        return await self._validate_token_or_none(token_data)

    async def inject_access(self, response: Response):
        if hasattr(self.request.state, "access_token"):
            access_token = self.request.state.access_token
            self.response = response

            await self._set_token(access_token, TokenType.ACCESS)

    async def refresh_access_token(self):
        refresh_data: TokenData = await self.read_token(TokenType.REFRESH)

        if not refresh_data:
            raise Exception(
                "Not valid refresh token"
            )

        token_data = {"sub": str(refresh_data.sub)}
        access = self.token_provider.create_access_token(token_data)

        self.request.state.access_token = access

        await self._set_token(access, TokenType.ACCESS)
        return access

    async def set_tokens(self, user: User):
        token_data = {"sub": str(user.id)}

        access = self.token_provider.create_access_token(token_data)
        refresh = self.token_provider.create_refresh_token(token_data)

        await self._set_token(access, TokenType.ACCESS)
        await self._set_token(refresh, TokenType.REFRESH)

    async def _set_token(self, token: str, token_type: TokenType):
        for transport in self.get_transports(transport_type=token_type):
            transport.set_token(self.response, token)

        if not self.token_storage:
            return None

        token_data = self.token_provider.token_read(token)
        if token_data:
            await self.token_storage.add_store_token(token_data)

    async def _validate_token_or_none(self, token_data: TokenData) -> None | TokenData:
        if not token_data:
            return None

        if self.token_storage and token_data.jti:
            is_active = await self.token_storage.is_active_token(token_data)
            if not is_active:
                return None

        return token_data

    def _get_access_token(self):
        for transport in self.get_transports(TokenType.ACCESS):
            if token := transport.get_token(self.request):
                return token

    def _get_refresh_token(self):
        for transport in self.get_transports(TokenType.REFRESH):
            if token := transport.get_token(self.request):
                return token

    def get_transports(self, transport_type: TokenType) -> list:
        for token_type, transports in self.transports.items():
            if token_type == transport_type:
                return transports

        return []
