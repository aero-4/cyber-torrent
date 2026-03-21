import abc

from src.users.domain.entities import TokenType, TokenData


class ITokenProvider(abc.ABC):

    def encode_token(self, token_data: TokenData) -> str:
        pass

    def decode_token(self, token: str) -> dict:
        pass

