from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/tiscord"

    JWT_SECRET: str = "changeme-in-production"
    JWT_ACCESS_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 30

    STORAGE_BACKEND: str = "local"  # "local" | "s3"
    STORAGE_LOCAL_PATH: str = "./uploads"
    STORAGE_S3_BUCKET: str = ""
    STORAGE_S3_ENDPOINT: str = ""
    STORAGE_S3_ACCESS_KEY: str = ""
    STORAGE_S3_SECRET_KEY: str = ""
    STORAGE_S3_REGION: str = "auto"

    STUN_URLS: str = "stun:stun.l.google.com:19302"
    TURN_URL: str = ""
    TURN_USER: str = ""
    TURN_PASS: str = ""

    MAX_ATTACHMENT_SIZE: int = 8 * 1024 * 1024  # 8 MB

    CORS_ORIGINS: str = "*"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
