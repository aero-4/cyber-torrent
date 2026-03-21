from typing import Annotated

from fastapi import Depends
from fastapi.openapi.models import Response
from starlette.requests import Request

from src.users.domain.interfaces.token_auth import ITokenAuth
from src.users.infrastructure.providers.jwt import JWTProvider
from src.users.infrastructure.services.auth_tokens import TokenAuth


def get_token_auth(request: Request = None, response: Response = None) -> ITokenAuth:
    jwt_provider = JWTProvider()

    return TokenAuth(request=request, response=response, provider=jwt_provider)


TokenAuthDep = Annotated[ITokenAuth, Depends(get_token_auth)]
