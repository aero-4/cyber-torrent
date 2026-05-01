import secrets
from typing import Literal

from dotenv import find_dotenv, load_dotenv
# from fastapi_csrf_protect import CsrfProtect
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn

ENV_FILE = find_dotenv()
load_dotenv(ENV_FILE)


class BaseAppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


class CsrfConfig(BaseAppConfig):
    secret_key: str = secrets.token_urlsafe(128)
    cookie_secure: bool = True
    cookie_samesite: str = "lax"
    token_location: Literal["body", "header"] = "body"
    token_key: str = "token_key"


class AuthConfig(BaseAppConfig):
    JWT_SECRET_KEY: str = "SECRET-KEY"
    JWT_SERVICE_ISSUER: str = "auth-service"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_HEADER_NAME: str = "Authorization"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 15
    REFRESH_HEADER_NAME: str = "X-Refresh-Token"
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 30
    TOKENS_HEADER_TYPE: str = "Bearer"


class OTPAuthConfig(BaseAppConfig):
    OTP_ISSUER: str = "Cyber"


class DatabaseConfig(BaseAppConfig):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_PORT: int

    @property
    def DATABASE_URI(self) -> str:
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        ))


class EmailConfig(BaseAppConfig):
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    TWO_FACTOR_EMAIL_MESSAGE_SUBJECT: str = "Confirm email"
    TWO_FACTOR_TOKEN_EXPIRE_SECONDS: int = 60 * 5
    CONFIRM_CODE_EMAIL_EXPIRE_SECONDS: int = 60 * 5
    USE_TLS: bool = True

    @property
    def TWO_FACTOR_EMAIL_MESSAGE_TEMPLATE(self):
        return """
Welcome to out service! Your confirm link email: {link}

Mail expired after {expire_minutes} minutes.
"""

    @property
    def CONFIRM_EMAIL_MESSAGE_TEMPLATE(self):
        return """
Welcome to out service! Your code: {code}

Mail expired after {expire_minutes} minutes.
"""


class AppConfig(BaseAppConfig):
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    APP_ROOT_PATH: str = "/api/v1"

    APP_USE_SSL: bool = False
    APP_DOMAIN: str | None = None

    @property
    def APP_URI(self):
        return f"http{'s' if self.APP_USE_SSL else ''}://{self.APP_HOST if not self.APP_USE_SSL else self.APP_DOMAIN}:{self.APP_PORT}"


class OAuth2Config(BaseAppConfig):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str


class MetadataConfig(BaseAppConfig):
    RAWGIO_API_TOKEN: str = ""



class TaskiqConfig(BaseAppConfig):
    RABBITMQ_URL: str
    RABBITMQ_BACKEND_RESULT: str


class RedisConfig(BaseAppConfig):
    REDIS_HOST: str
    REDIS_PORT: int


class Config(BaseAppConfig):
    auth: AuthConfig = AuthConfig()
    database: DatabaseConfig = DatabaseConfig()
    csrf: CsrfConfig = CsrfConfig()
    otp: OTPAuthConfig = OTPAuthConfig()
    email: EmailConfig = EmailConfig()
    app: AppConfig = AppConfig()
    oauth2: OAuth2Config = OAuth2Config()
    metadata: MetadataConfig = MetadataConfig()
    taskiq: TaskiqConfig = TaskiqConfig()
    redis: RedisConfig = RedisConfig()


# @CsrfProtect.load_config
# def get_csrf_config():
#     return CsrfConfig()


config = Config()
