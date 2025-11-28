from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger


# مسیر ریشه پروژه (طبق تست: parents[4])
PROJECT_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    # Database
    DATABASE_DIALECT: str
    DATABASE_HOSTNAME: str
    DATABASE_NAME: str
    DATABASE_PASSWORD: str
    DATABASE_PORT: int
    DATABASE_USERNAME: str

    # Global settings
    DEBUG_MODE: bool

    # Redis
    REDIS_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # OTP
    OTP_EXPIRE_TIME: int

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8"
    )


@lru_cache
@logger.catch
def get_settings() -> Settings:
    return Settings()
