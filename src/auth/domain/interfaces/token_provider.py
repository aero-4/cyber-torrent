import abc

from src.auth.domain.entities import TokenData


class ITokenProvider(abc.ABC):

    def create_access_token(self, token_data: TokenData) -> str:
        pass

    def create_refresh_token(self, token_data: TokenData) -> str:
        pass

    def encode_token(self, payload: dict, expires: int) -> str:
        pass

    def decode_token(self, token: str) -> dict:
        pass

