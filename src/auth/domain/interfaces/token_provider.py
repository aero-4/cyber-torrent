import abc

from src.auth.domain.entities import TokenData


class ITokenProvider(abc.ABC):

    def token_read(self, token: str) -> TokenData:
        pass

    def create_access_token(self, data: dict) -> str:
        pass

    def create_refresh_token(self, data: dict) -> str:
        pass


