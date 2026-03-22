from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.entities import TokenType
from src.users.domain.entities import *
from src.users.infrastructure.db.uow import UsersUnitOfWork
from src.auth.presentation.dependencies import get_token_auth


class AuthorizationMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        auth = get_token_auth(request)
        access_token_data = await auth.read_token(TokenType.ACCESS)
        if access_token_data:
            try:
                uow = UsersUnitOfWork()
                async with uow:
                    if user := await uow.users.get_by_id(access_token_data.id):
                        request.state.user = user
            except:
                request.state.user = AnonymousUser()

        response = await call_next(request)
        return response


class RefreshMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # auth = get_token_auth(request=request)

        response = await call_next(request)

        auth = get_token_auth(request=request, response=response)

        if not await auth.read_token(TokenType.ACCESS):
            try:
                access_token = await auth.refresh_access_token()
                print(f"Token refreshed: {access_token}")
            except:
                pass

        return response
