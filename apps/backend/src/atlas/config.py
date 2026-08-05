"""Typed runtime configuration with secret-safe field types."""

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ATLAS settings loaded from environment variables or an untracked local file."""

    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    atlas_env: Literal["development", "test", "production"] = "development"
    atlas_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    database_url: SecretStr = SecretStr(
        "postgresql+psycopg://atlas:atlas-local-only@localhost:5432/atlas"
    )
    web_origin: AnyHttpUrl = AnyHttpUrl("http://localhost:3000")
    api_origin: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")

    openai_api_key: SecretStr | None = None
    atlas_visitor_hmac_secret: SecretStr | None = None
    atlas_operator_token: SecretStr | None = None

    atlas_answer_model: str = "gpt-5.6-luna"
    atlas_reasoning_effort: Literal["low", "medium", "high"] = "medium"
    atlas_embedding_model: str = "text-embedding-3-small"
    atlas_embedding_dimensions: int = Field(default=1536, ge=1)
    atlas_anonymous_answer_limit: int = Field(default=10, ge=1)
    atlas_anonymous_window_hours: int = Field(default=24, ge=1)
    atlas_content_retention_days: int = Field(default=30, ge=1)


@lru_cache
def get_settings() -> Settings:
    """Return one immutable settings instance per process."""

    return Settings()
