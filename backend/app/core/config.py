from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Aivanta OS API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./aivanta.db"
    cors_origins: str = "http://localhost:3000"

    # AI settings are reserved for Phase 3 and remain backend-only.
    ai_provider: str = "9router"
    ai_base_url: str = "http://localhost:20128/v1"
    ai_api_key: str = ""
    ai_model: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
