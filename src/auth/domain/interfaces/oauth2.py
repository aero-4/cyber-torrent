import abc

from src.auth.domain.interfaces.token_auth import ITokenProvider
from src.core.domain.exceptions import BadRequest


class IOauth2Provider(abc.ABC):

    def __init__(self, token_provider: ITokenProvider):
        self.token_provider = token_provider

    def generate_redirect_uri(self):
        pass

    async def callback(self, code: str):
        pass

    def parse_data(self, data: dict, name: str):
        token_data = data.get(name)
        if not token_data:
            raise BadRequest(message=f"No '{name}' in response data")

        try:
            id_data = self.token_provider.decode_jwt_without_secret(token_data)
        except Exception as e:
            raise BadRequest(message="Unreadable user data")
        return id_data
