import secrets
from typing import Literal

from dotenv import find_dotenv
from fastapi_csrf_protect import CsrfProtect
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = find_dotenv()


class CsrfConfig(BaseSettings):
    secret_key: str = secrets.token_urlsafe(128)
    cookie_secure: bool = True
    cookie_samesite: str = "lax"
    token_location: Literal["body", "header"] = "body"
    token_key: str = "token_key"


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE
    )

    JWT_SECRET_KEY: str = secrets.token_urlsafe(256)
    JWT_SERVICE_ISSUER: str = "auth-service"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 15
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 30


class DatabaseConfig(BaseSettings):
    DATABASE_URI: str = "sqlite+aiosqlite:///test.db"


class Config(BaseSettings):
    auth: AuthConfig = AuthConfig()
    database: DatabaseConfig = DatabaseConfig()
    csrf: CsrfConfig = CsrfConfig()


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfConfig()


config = Config()
