from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ALLOWED_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://localhost:5173",
    "https://pakit.kr",
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PAKIT_",
        extra="ignore",
    )

    app_name: str = "Pakit API"
    environment: Literal["local", "test", "staging", "production"] = "local"
    debug: bool = False
    api_prefix: str = "/api"


@lru_cache
def get_settings() -> Settings:
    return Settings()
