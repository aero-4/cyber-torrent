import datetime
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from time import perf_counter

from starlette.responses import JSONResponse, Response
from starlette.middleware.cors import CORSMiddleware
from starlette.templating import Jinja2Templates
from starlette_csrf import CSRFMiddleware

from src.auth.presentation.middlewares import AuthorizationMiddleware, RefreshMiddleware
from src.auth.presentation.api import router as auth_api_router
from src.core.infrastructure.setup_logging import setup_logging
from src.users.presentation.api import router as users_api_router
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

    logger.debug(
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
