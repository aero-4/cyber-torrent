import datetime
import logging
import uuid

from jose.jwt import encode, decode
from jose.exceptions import JWTError
from src.core.config import config
from src.auth.domain.entities import TokenData
from src.auth.domain.interfaces.token_auth import ITokenProvider


class JwtProvider(ITokenProvider):

    def create_access_token(self, data: dict) -> str:
        return self._encode_jwt(data, config.auth.ACCESS_TOKEN_EXPIRE_SECONDS)

    def create_refresh_token(self, data: dict) -> str:
        return self._encode_jwt(data, config.auth.REFRESH_TOKEN_EXPIRE_SECONDS)

    def token_read(self, token: str) -> None | TokenData:
        if not token:
            return None

        try:
            token_data = self._decode_jwt(token=token)
            if not token_data.get("sub"):
                return None

            return TokenData(**token_data)

        except JWTError as exp:
            return None

    def _encode_jwt(self, payload: dict, expires: int, secret_key: str = config.auth.JWT_SECRET_KEY, algorithm: str = config.auth.JWT_ALGORITHM) -> str:
        payload["iss"] = config.auth.JWT_SERVICE_ISSUER  # creator name OR site
        payload["exp"] = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(seconds=expires)  # expire
        payload["iat"] = datetime.datetime.now(tz=datetime.UTC)  # create now
        payload["jti"] = str(uuid.uuid4())  # id

        token = encode(
            claims=payload,
            key=secret_key,
            algorithm=algorithm,
        )
        return token

    def _decode_jwt(self, token: str, secret_key: str = config.auth.JWT_SECRET_KEY, algorithm: str = config.auth.JWT_ALGORITHM) -> dict:
        payload = decode(
            token,
            key=secret_key,
            algorithms=[algorithm]
        )
        return payload

    def decode_jwt_without_secret(self, token: str) -> dict:
        payload = decode(token, key=None, options={
            "verify_signature": False,  # ОБЯЗАТЕЛЬНО TRUE
            "verify_at_hash": False,  # Можно False, если не проверяешь соответствие access токену
            "verify_aud": False,  # Не проверять поле audience (исправляет твою ошибку)
            "verify_exp": False
        }, algorithms=["RS256"], audience=config.oauth2.GOOGLE_CLIENT_ID)
        return payload
