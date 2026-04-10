import secrets
from typing import Literal

from dotenv import find_dotenv, load_dotenv
from fastapi_csrf_protect import CsrfProtect
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = find_dotenv()
load_dotenv(ENV_FILE)


# 1. Create a Base Configuration Class
class BaseAppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",  # This prevents the extra_forbidden errors
    )


# 2. Inherit from BaseAppConfig instead of BaseSettings
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
    OTP_SECRET: str = secrets.token_urlsafe(32)
    OTP_ISSUER: str = "JwtAuthAPP"


class DatabaseConfig(BaseAppConfig):
    DATABASE_URI: str = "sqlite+aiosqlite:///test.db"


class EmailConfig(BaseAppConfig):
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 465
    EMAIL_USERNAME: str = "dimongames6@gmail.com"
    EMAIL_PASSWORD: str = "jtvz npox gxuc sasx"
    TWO_FACTOR_EMAIL_MESSAGE_SUBJECT: str = "2fa confirm email"
    TWO_FACTOR_EMAIL_MESSAGE_TEMPLATE: str = """
Welcome to out service!    

Your confirm link email: {link}
"""
    TWO_FACTOR_TOKEN_EXPIRE_SECONDS: int = 60 * 30
    USE_TLS: bool = True


class AppConfig(BaseAppConfig):
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    USE_SSL: bool = False

    @property
    def APP_URI(self):
        return f"http{'s' if self.USE_SSL else ''}://{self.HOST}:{self.PORT}"


class OAuth2Config(BaseAppConfig):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str


class MetadataConfig(BaseAppConfig):
    RAWGIO_API_TOKEN: str = ""


class CeleryConfig(BaseAppConfig):
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str


class Config(BaseAppConfig):
    auth: AuthConfig = AuthConfig()
    database: DatabaseConfig = DatabaseConfig()
    csrf: CsrfConfig = CsrfConfig()
    otp: OTPAuthConfig = OTPAuthConfig()
    email: EmailConfig = EmailConfig()
    app: AppConfig = AppConfig()
    oauth2: OAuth2Config = OAuth2Config()
    celery: CeleryConfig = CeleryConfig()


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfConfig()


config = Config()
