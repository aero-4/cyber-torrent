import datetime

from jose.jwt import encode, decode

from src.core.config import config
from src.auth.domain.entities import TokenData
from src.auth.domain.interfaces.token_provider import ITokenProvider


class JWTProvider(ITokenProvider):

    def create_access_token(self, token_data: TokenData):
        return self.encode_token(token_data.payload, config.auth.ACCESS_TOKEN_EXPIRE_SECONDS)

    def create_refresh_token(self, token_data: TokenData):
        return self.encode_token(token_data.payload, config.auth.REFRESH_TOKEN_EXPIRE_SECONDS)

    def encode_token(self, payload: dict, expires: int, secret_key: str = config.auth.JWT_SECRET_KEY, algorithm: str = config.auth.JWT_ALGORITHM) -> str:
        payload = payload.copy()

        payload["exp"] = (datetime.datetime.now() + datetime.timedelta(seconds=expires)).astimezone()
        token = encode(
            claims=payload,
            key=secret_key,
            algorithm=algorithm,
        )
        return token

    def decode_token(self, token: str, secret_key: str = config.auth.JWT_SECRET_KEY, algorithm: str = config.auth.JWT_ALGORITHM) -> dict:
        try:
            payload = decode(
                token,
                key=secret_key,
                algorithms=[algorithm]
            )

            return payload
        except Exception as e:
            raise Exception("Not valid jwt token") from e
