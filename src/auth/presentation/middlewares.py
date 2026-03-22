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
            except Exception as e:
                request.state.user = AnonymousUser()

        response = await call_next(request)
        return response
