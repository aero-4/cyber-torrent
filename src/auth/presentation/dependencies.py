from typing import Annotated

from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.entities import TokenType
from src.auth.domain.interfaces.hasher import IHasherProvider
from src.auth.domain.interfaces.qrcode import IQrCodeProvider
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.domain.interfaces.token_auth import ITokenProvider, ITokenStorage
from src.auth.infrastructure.providers.hasher import HasherProvider
from src.auth.infrastructure.providers.jwt import JwtProvider
from src.auth.infrastructure.providers.qr import QrCodeProvider
from src.auth.infrastructure.providers.redis_storage import RedisTokenStorage
from src.auth.infrastructure.services.auth_tokens import TokenAuth
from src.auth.infrastructure.transports.cookie import CookiesTransport
from src.auth.infrastructure.transports.header import HeadersTransport
from src.core.config import config


def get_hasher_provide() -> IHasherProvider:
    return HasherProvider()


def get_jwt_provider() -> ITokenProvider:
    return JwtProvider()


def get_redis_storage() -> ITokenStorage:
    return RedisTokenStorage()


def get_qrcode_provide() -> IQrCodeProvider:
    return QrCodeProvider()


def get_token_auth(request: Request = None,
                   response: Response = None) -> TokenAuth:
    transports = {
        TokenType.ACCESS:
            [CookiesTransport(TokenType.ACCESS,
                              max_age=config.auth.ACCESS_TOKEN_EXPIRE_SECONDS),
             HeadersTransport(config.auth.ACCESS_HEADER_NAME,
                              config.auth.TOKENS_HEADER_TYPE)],
        TokenType.REFRESH:
            [CookiesTransport(TokenType.REFRESH,
                              max_age=config.auth.REFRESH_TOKEN_EXPIRE_SECONDS),
             HeadersTransport(config.auth.REFRESH_HEADER_NAME,
                              config.auth.TOKENS_HEADER_TYPE)]
    }
    return TokenAuth(request=request,
                     response=response,
                     token_storage=get_redis_storage(),
                     provider=get_jwt_provider(),
                     transports=transports)


TokenAuthDep = Annotated[ITokenAuth, Depends(get_token_auth)]
HasherProvideDep = Annotated[IHasherProvider, Depends(get_hasher_provide)]
RedisStorageDep = Annotated[ITokenStorage, Depends(get_redis_storage)]
QrProvideDep = Annotated[IQrCodeProvider, Depends(get_qrcode_provide)]
