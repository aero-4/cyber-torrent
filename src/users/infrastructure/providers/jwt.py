import datetime

from jose.jwt import encode, decode

from src.core.config import config
from src.users.domain.entities import TokenType, TokenData
from src.users.domain.interfaces.token_provider import ITokenProvider


class JWTProvider(ITokenProvider):

    def encode_token(self, token_data: TokenData, secret_key: str = config.auth.JWT_SECRET_KEY, algorithm: str = config.auth.JWT_ALGORITHM) -> str:
        payload = {}
        if token_data.payload:
            payload = token_data.payload.copy()

        payload["type"] = token_data.type
        payload["exp"] = datetime.datetime.now() + datetime.timedelta(
            minutes=config.auth.EXPIRE_ACCESS_TOKEN_MIN if token_data.type == TokenType.access_token else config.auth.EXPIRE_REFRESH_TOKEN_MIN
        )
        payload["sub"] = token_data.user_id

        token = encode(
            claims=payload,
            key=secret_key,
            algorithm=algorithm,
        )

        return token

    def decode_token(self, token: str, secret_key: str = config.auth.JWT_SECRET_KEY, algorithm: str = config.auth.JWT_ALGORITHM) -> dict:
        payload = decode(
            token,
            key=secret_key,
            algorithms=[algorithm]
        )

        return payload
