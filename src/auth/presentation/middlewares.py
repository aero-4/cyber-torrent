from fastapi import HTTPException, Depends
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import TokenValidationError
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp

from src.auth.domain.entities import TokenType
from src.core.config import get_csrf_config, config
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
                    if user := await uow.users.get_by_id(access_token_data.sub):
                        request.state.user = user or AnonymousUser()
            except Exception as e:
                print(e)
                request.state.user = AnonymousUser()

        response = await call_next(request)
        return response


class RefreshMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        pre_auth = get_token_auth(request)
        access_data = await pre_auth.read_token(TokenType.ACCESS)
        if not access_data:
            try:
                await pre_auth.refresh_access_token()
            except:
                pass

        response = await call_next(request)

        post_auth = get_token_auth(request=request, response=response)
        refresh_data = await post_auth.read_token(TokenType.REFRESH)
        if refresh_data:
            await post_auth.inject_access(response)

        return response

#
# class CsrfProtectMiddleware(BaseHTTPMiddleware):
#
#     async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
#         csrf_protect = CsrfProtect()
#
#         if request.cookies.get(config.csrf.cookie_key):
#             try:
#                 await csrf_protect.validate_csrf(request)
#             except Exception as e:
#                 print(e)
#                 return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
#                                     content="CSRF token not valid")
#
#         response = await call_next(request)  # запрос уже сделан
#
#         if not request.cookies.get(config.csrf.cookie_key):
#             csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
#             csrf_protect.set_csrf_cookie(csrf_signed_token=signed_token, response=response)
#             response.headers[config.csrf.header_name] = config.csrf.header_type + csrf_token
#
#         return response
