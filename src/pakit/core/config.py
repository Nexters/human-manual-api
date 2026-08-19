from datetime import datetime
from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import SecretStr
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
        env_ignore_empty=True,
        extra="ignore",
    )

    app_name: str = "Pakit API"
    environment: Literal["local", "test", "staging", "production"] = "local"
    debug: bool = False
    api_prefix: str = "/api"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "pakit"
    database_user: str = "pakit"
    database_password: SecretStr = SecretStr("")
    admin_username: str | None = None
    admin_password: SecretStr | None = None
    usage_tracking_started_at: datetime | None = None

    @property
    def database_url(self) -> str:
        password = quote_plus(self.database_password.get_secret_value())
        user = quote_plus(self.database_user)
        return (
            f"postgresql+asyncpg://{user}:{password}@{self.database_host}:"
            f"{self.database_port}/{self.database_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
