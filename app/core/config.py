"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Values come from environment variables or `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Personal Assistant"
    app_version: str = "0.1.0"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    secret_key: str = "local-dev-secret-change-me"
    access_token_expire_minutes: int = 30

    database_url: str = "sqlite:///./data/assistant.db"
    cors_origins: str = "http://localhost:5173"
    api_key: str | None = None
    max_context_messages: int = 20
    frontend_url: str = "http://localhost:5173"

    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str = "http://127.0.0.1:8000/api/v1/calendar/callback"

    otel_exporter_otlp_endpoint: str | None = None

    @field_validator("database_url", mode="before")
    @classmethod
    def use_local_database_when_blank(cls, value: str | None) -> str:
        return value or "sqlite:///./data/assistant.db"


    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
