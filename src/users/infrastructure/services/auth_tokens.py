from abc import ABC

from starlette.requests import Request
from starlette.responses import Response

from src.users.domain.entities import TokenType, TokenData, TokenPair
from src.users.domain.interfaces.token_auth import ITokenAuth
from src.users.domain.interfaces.token_provider import ITokenProvider
from src.users.infrastructure.db.orm import UsersOrm


class TokenAuth(ITokenAuth, ABC):

    def __init__(self, request: Request, provider: ITokenProvider, response: Response = None):
        self.response = response
        self.request = request
        self.provider = provider


    def read_token(self):
        pass

    def set_tokens(self, user_id: int):
        tokens = TokenPair(access=self.provider.encode_token(TokenData(user_id=user_id, type=TokenType.access_token)),
                           refresh=self.provider.encode_token(TokenData(user_id=user_id, type=TokenType.refresh_token)))

        if self.response:
            self.set_cookies(tokens)

        self.set_headers(tokens)

        return tokens

    def set_cookies(self, tokens: TokenPair):
        self.response.set_cookie(
            "access_token", tokens.access
        )
        self.response.set_cookie(
            "refresh_token", tokens.refresh
        )

    def set_headers(self, tokens: TokenPair):
        self.response.headers["Authorization"] = f"Bearer {tokens.access}"
