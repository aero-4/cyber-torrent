import datetime
import logging

from fastapi import FastAPI

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.middleware.cors import CORSMiddleware
from starlette_csrf import CSRFMiddleware

from src.auth.presentation.middlewares import AuthorizationMiddleware, RefreshMiddleware
from src.auth.presentation.api import router as auth_api_router
from src.users.presentation.api import router as users_api_router
from typing import Dict, Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from src.core.domain.exceptions import AppException

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


def create_error_response(
        status_code: int,
        message: str,
        details: Dict[str, Any] = None,
        request_id: str = None
) -> Dict[str, Any]:
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        408: "REQUEST_TIMEOUT",
        409: "CONFLICT",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT"
    }
    response = {
        "success": False,
        "error": {
            "code": error_code_map.get(status_code, "INTERNAL_ERROR"),
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

    return JSONResponse(status_code=exc.status_code,
                        content=create_error_response(
                            status_code=exc.status_code,
                            message=exc.message,
                            details=exc.details
                        ))


class CustomResponseCSRFMiddleware(CSRFMiddleware):
    def _get_error_response(self, request: Request) -> Response:
        return JSONResponse(
            content={"code": "Not valid csrf-token"}, status_code=403
        )
