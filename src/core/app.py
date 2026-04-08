import datetime
import logging
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI
from time import perf_counter

from fastapi_csrf_protect import CsrfProtect
from sqladmin import Admin
from starlette.responses import Response
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette_csrf import CSRFMiddleware

from src.auth.presentation.middlewares import AuthorizationMiddleware, RefreshMiddleware
from src.auth.presentation.api import router as auth_api_router

from views.home.home import router as home_view
from views.login.login import router as login_view
from views.register.register import router as register_view
from views.profile.profile import router as profile_view
from views.faq.faq import router as faq_view

from src.core.infrastructure.setup_logging import setup_logging
from src.db.engine import engine
from src.users.infrastructure.db.orm import UsersAdmin
from src.users.presentation.api import router as users_api_router
from src.torrents.presentation.api import router as torrents_api_router
from typing import Dict, Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from src.core.domain.exceptions import AppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


logger = logging.getLogger(__name__)
app = FastAPI(lifespan=lifespan)
admin = Admin(app, engine=engine)
# csrf_protect = CsrfProtect()

admin.add_view(UsersAdmin)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


async def get_secret(user_id: str = None):
    return str(secrets.token_urlsafe(64))


# app.add_middleware(TwoFactorMiddleware,
#                    get_user_secret_callback=get_secret,
#                    excluded_paths=["/docs", "/auth/qr"],
#                    header_name="X-2FA-Code",)
# encryption_key=base64.b64encode(secrets.token_bytes(32))  # Optional)
app.add_middleware(RefreshMiddleware)
app.add_middleware(AuthorizationMiddleware)

# app.add_middleware(CSRFMiddleware, secret=config.csrf.secret_key)

# views
app.include_router(router=home_view)
app.include_router(router=register_view)
app.include_router(router=login_view)
app.include_router(router=profile_view)
app.include_router(router=faq_view)

# api
app.include_router(router=auth_api_router, prefix="/auth", tags=["Auth"])
app.include_router(router=users_api_router, prefix="/users", tags=["Users"])
app.include_router(router=torrents_api_router, prefix="/torrents", tags=["Torrents"])


def create_error_response(
        message: str,
        error_code: str,
        details: Dict[str, Any] = None,
        request_id: str = None
) -> Dict[str, Any]:
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.datetime.now().isoformat()
        }
    }

    if details:
        response["error"]["details"] = details

    if request_id:
        response["error"]["request_id"] = request_id

    return response


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logging.warning(
        f"Application error: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details
        }
    )
    content_error = create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details
    )
    return JSONResponse(status_code=exc.status_code,
                        content=content_error)


@app.middleware("http")
async def logging_requests(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    duration_ms = (perf_counter() - start) * 1000

    logger.info(
        "HTTP request completed",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "details": f"- {duration_ms:.2f}ms",
        },
    )
    return response


class CustomResponseCSRFMiddleware(CSRFMiddleware):
    def _get_error_response(self, request: Request) -> Response:
        return JSONResponse(
            content={"code": "Not valid csrf-token"}, status_code=403
        )
