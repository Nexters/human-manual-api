from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PRODUCTION_FRONTEND_ORIGIN = "https://pakit.kr"


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
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", PRODUCTION_FRONTEND_ORIGIN]
    )

    @property
    def allowed_cors_origins(self) -> list[str]:
        """운영 프론트와 환경별 추가 origin을 중복 없이 반환합니다."""
        return list(dict.fromkeys([*self.cors_origins, PRODUCTION_FRONTEND_ORIGIN]))


@lru_cache
def get_settings() -> Settings:
    return Settings()
