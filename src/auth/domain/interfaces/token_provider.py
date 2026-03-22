import abc

from src.auth.domain.entities import TokenData


class ITokenProvider(abc.ABC):

    def read_token(self, token: str) -> TokenData:
        pass

    def create_access_token(self, token_data: TokenData) -> str:
        pass

    def create_refresh_token(self, token_data: TokenData) -> str:
        pass


