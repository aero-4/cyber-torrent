from fastapi import FastAPI

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.middleware.cors import CORSMiddleware
from starlette_csrf import CSRFMiddleware

from src.auth.presentation.middlewares import AuthorizationMiddleware, RefreshMiddleware
from src.auth.presentation.api import router as auth_api_router
from src.core.config import config
from src.users.presentation.api import router as users_api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthorizationMiddleware)
app.add_middleware(RefreshMiddleware)
# app.add_middleware(CSRFMiddleware, secret=config.csrf.secret_key)

app.include_router(router=auth_api_router, prefix="/auth", tags=["Auth"])
app.include_router(router=users_api_router, prefix="/users", tags=["Users"])


class CustomResponseCSRFMiddleware(CSRFMiddleware):
    def _get_error_response(self, request: Request) -> Response:
        return JSONResponse(
            content={"code": "Not valid csrf-token"}, status_code=403
        )
