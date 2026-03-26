from typing import Annotated

from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.entities import TokenType
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.infrastructure.providers.jwt import JWTProvider
from src.auth.infrastructure.providers.redis_storage import RedisTokenStorage
from src.auth.infrastructure.services.auth_tokens import TokenAuth
from src.auth.infrastructure.transports.cookie import CookiesTransport
from src.auth.infrastructure.transports.header import HeadersTransport
from src.core.config import config


def get_token_auth(request: Request = None,
                   response: Response = None) -> TokenAuth:
    jwt_provider = JWTProvider()
    token_storage = RedisTokenStorage()

    transports = {
        TokenType.ACCESS: [CookiesTransport(TokenType.ACCESS,
                                            max_age=config.auth.ACCESS_TOKEN_EXPIRE_SECONDS),
                           HeadersTransport(config.auth.ACCESS_HEADER_NAME,
                                            config.auth.TOKENS_HEADER_TYPE)],
        TokenType.REFRESH: [CookiesTransport(TokenType.REFRESH,
                                             max_age=config.auth.REFRESH_TOKEN_EXPIRE_SECONDS),
                            HeadersTransport(config.auth.REFRESH_HEADER_NAME,
                                             config.auth.TOKENS_HEADER_TYPE)]
    }

    return TokenAuth(request=request,
                     response=response,
                     token_storage=token_storage,
                     provider=jwt_provider,
                     transports=transports)


TokenAuthDep = Annotated[ITokenAuth, Depends(get_token_auth)]
