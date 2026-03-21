from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = find_dotenv()


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE
    )

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    EXPIRE_ACCESS_TOKEN_MIN: int = 15
    EXPIRE_REFRESH_TOKEN_MIN: int = 60 * 60


class Config(BaseSettings):
    auth: AuthConfig = AuthConfig()


config = Config()
