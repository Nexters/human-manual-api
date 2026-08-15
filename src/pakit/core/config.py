from functools import lru_cache
from typing import Literal

from pydantic import Field
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

    # Database
    postgres_user: str = Field(default="pakit", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default="", validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="pakit", validation_alias="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
