import datetime
import logging
from typing import Dict, Any

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.core.app import app
from src.core.domain.exceptions import AppException


def create_error_response(
        status_code: int,
        error_code: str,
        message: str,
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
        f"Application error: {exc.error_code} - {exc.message}",
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
                            error_code=exc.error_code,
                            message=exc.message,
                            details=exc.details
                        ))

# @app.exception_handler(HTTPException)
# async def app_http_exceptions_handler(request: Request, exc: HTTPException):
#     return JSONResponse(status_code=exc.status_code,
#                         content=create_error_response(
#                             status_code=exc.status_code,
#                             message=exc.detail,
#                         ))
