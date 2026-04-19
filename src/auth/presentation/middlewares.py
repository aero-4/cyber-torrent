from fastapi import HTTPException, Depends
# from fastapi_csrf_protect import CsrfProtect
# from fastapi_csrf_protect.exceptions import TokenValidationError
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp

from src.auth.domain.entities import TokenType
from src.core.config import config
from src.users.domain.entities import *
from src.users.infrastructure.db.uow import UsersUnitOfWork
from src.auth.presentation.dependencies import get_token_auth


class AuthorizationMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        auth = get_token_auth(request)
        try:
            access_token_data = await auth.read_token(TokenType.ACCESS)
            if access_token_data:
                uow = UsersUnitOfWork()
                async with uow:
                    if user := await uow.users.get_by_id(access_token_data.sub):
                        request.state.user = user or AnonymousUser()
        except Exception as e:
            request.state.user = AnonymousUser()

        response = await call_next(request)
        return response


class RefreshMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        pre_auth = get_token_auth(request)
        try:
            access_data = await pre_auth.read_token(TokenType.ACCESS)
            if not access_data:
                await pre_auth.refresh_access_token()
        except:
            pass

        response = await call_next(request)

        try:
            post_auth = get_token_auth(request=request, response=response)

            refresh_data = await post_auth.read_token(TokenType.REFRESH)
            if refresh_data:
                await post_auth.inject_access(response)
        except:
            pass

        return response


