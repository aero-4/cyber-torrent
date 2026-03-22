from typing import Annotated

from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.infrastructure.providers.jwt import JWTProvider
from src.auth.infrastructure.services.auth_tokens import TokenAuth


def get_token_auth(request: Request = None,
                   response: Response = None) -> TokenAuth:
    jwt_provider = JWTProvider()

    return TokenAuth(request=request,
                     response=response,
                     provider=jwt_provider)


TokenAuthDep = Annotated[ITokenAuth, Depends(get_token_auth)]
