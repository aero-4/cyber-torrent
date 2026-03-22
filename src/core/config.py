import secrets

from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = find_dotenv()


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


config = Config()
