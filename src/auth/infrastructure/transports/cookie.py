from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.interfaces.transport import IAuthTransport


class CookiesTransport(IAuthTransport):

    def __init__(self, cookie_name: str):
        self.cookie_name = cookie_name

    def get_token(self, request: Request) -> str | None:
        return request.cookies.get(self.cookie_name, None)

    def set_token(self, response: Response, token: str) -> None:
        response.set_cookie(
            self.cookie_name,
            token
        )

    def delete_token(self, response: Response) -> None:
        response.delete_cookie(self.cookie_name)
