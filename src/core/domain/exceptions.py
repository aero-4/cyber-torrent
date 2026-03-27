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


class AuthRequired(AppException):
    message = "Authentication required"
    error_code = ERROR_CODES.get(401)
    status_code = 401


class AlreadyExists(AppException):
    message = "Already exists"
    error_code = ERROR_CODES.get(409)
    status_code = 409


class BadRequest(AppException):
    message = "Bad request"
    error_code = ERROR_CODES.get(400)
    status_code = 400


class NotFound(AppException):
    message = "Not found"
    error_code = ERROR_CODES.get(404)
    status_code = 404
