from typing import Optional, Dict, Any
from src.core.domain.entities import ERROR_CODES
from starlette import status


class AppException(Exception):
    message: str = "Server invalid"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "INTERNAL ERROR"
    details: dict | None = {}

    def __init__(self,
                 message: str | None = None,
                 status_code: int | None = None,
                 error_code: str | None = None,
                 details: Optional[Dict[str, Any]] = None):
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        self.error_code = error_code or self.error_code
        self.details = details or self.details

        super().__init__(self.message,
                         self.status_code,
                         self.error_code,
                         self.details)




class AlreadyExists(AppException):
    message = "Already exists"
    status_code = 409
    error_code = ERROR_CODES.get(status_code)


class BadRequest(AppException):
    message = "Bad request"
    status_code = 400
    error_code = ERROR_CODES.get(status_code)


class NotFound(AppException):
    message = "Not found"
    status_code = 404
    error_code = ERROR_CODES.get(status_code)
