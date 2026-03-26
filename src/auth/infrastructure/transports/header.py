from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.interfaces.transport import IAuthTransport


class HeadersTransport(IAuthTransport):

    def __init__(self,
                 header_name: str = None,
                 header_type: str = None):

        self.header_name = header_name
        self.header_type = header_type

    def get_token(self, request: Request) -> str | None:
        header = request.headers.get(self.header_name, None)
        if header:
            try:
                return header.split(" ")[1]
            except:
                return None

    def set_token(self, response: Response, token: str, **kwargs) -> None:
        response.headers[self.header_name] = f"{self.header_type} {token}" if self.header_type else token

    def delete_token(self, response: Response):
        response.headers[self.header_name] = ""
