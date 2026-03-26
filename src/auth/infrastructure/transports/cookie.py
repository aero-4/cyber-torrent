from datetime import datetime

from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.interfaces.transport import IAuthTransport


class CookiesTransport(IAuthTransport):

    def __init__(self,
                 cookie_name: str,
                 max_age: int,
                 domain: str = None,
                 secure: bool = False,
                 httponly: bool = False,
                 samesite: str = "lax"):
        self.max_age = max_age
        self.domain = domain
        self.secure = secure
        self.httponly = httponly
        self.samesite = samesite
        self.cookie_name = cookie_name

    def get_token(self, request: Request) -> str | None:
        return request.cookies.get(self.cookie_name, None)

    def set_token(self, response: Response, token: str, **kwargs) -> None:
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            max_age=self.max_age,
            domain=self.domain,
            secure=self.secure,
            expires=kwargs.get("expires"),
            samesite=self.samesite,
        )

    def delete_token(self, response: Response) -> None:
        response.delete_cookie(self.cookie_name)
