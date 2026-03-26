from typing import Optional, Dict, Any


class AppException(Exception):

    def __init__(self, message: str, status_code: int = 500, error_code: str = "INTERNAL ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}

        super().__init__(self.details)



