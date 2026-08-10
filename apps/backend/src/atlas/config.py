"""Typed runtime configuration with secret-safe field types."""

from functools import lru_cache
from pathlib import Path
from typing import Literal, TypedDict

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SafeSettingsSummary(TypedDict):
    """Non-sensitive configuration fields that may be attached to logs or diagnostics."""

    environment: str
    log_level: str
    answer_model: str
    reasoning_effort: str
    embedding_model: str
    embedding_dimensions: int
    anonymous_answer_limit: int
    anonymous_comparison_limit: int
    anonymous_window_hours: int
    content_retention_days: int
    web_origin: str
    api_origin: str


class Settings(BaseSettings):
    """ATLAS settings loaded from environment variables or an untracked local file."""

    model_config = SettingsConfigDict(
        env_file=(
            ".env.local",
            ".env",
            str(Path(__file__).resolve().parents[4] / ".env.local"),
            str(Path(__file__).resolve().parents[4] / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    atlas_env: Literal["development", "test", "preview", "staging", "production"] = "development"
    atlas_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    database_url: SecretStr = SecretStr(
        "postgresql+psycopg://atlas:atlas-local-only@localhost:55432/atlas"
    )
    web_origin: AnyHttpUrl = AnyHttpUrl("http://localhost:3000")
    api_origin: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")

    openai_api_key: SecretStr | None = None
    atlas_visitor_hmac_secret: SecretStr | None = None
    atlas_operator_token: SecretStr | None = None
    langsmith_tracing: bool = False
    langsmith_api_key: SecretStr | None = None
    langsmith_project: str = "atlas-ai"
    langsmith_endpoint: AnyHttpUrl | None = None
    langsmith_workspace_id: str | None = None

    atlas_answer_model: str = "gpt-5.6-luna"
    atlas_reasoning_effort: Literal["low", "medium", "high"] = "medium"
    atlas_embedding_model: str = "text-embedding-3-small"
    atlas_embedding_dimensions: int = Field(default=1536, ge=1)
    atlas_anonymous_answer_limit: int = Field(default=10, ge=1)
    atlas_anonymous_comparison_limit: int = Field(default=5, ge=1)
    atlas_anonymous_window_hours: int = Field(default=24, ge=1)
    atlas_content_retention_days: int = Field(default=30, ge=1)
    atlas_news_enabled: bool = True
    atlas_auth_enabled: bool = True
    atlas_private_upload_max_bytes: int = Field(default=10_485_760, ge=1)
    atlas_private_retention_days: int = Field(default=30, ge=1)
    atlas_ingestion_refresh_min_hours: int = Field(default=6, ge=6, le=24)
    atlas_ingestion_refresh_max_hours: int = Field(default=24, ge=6, le=24)
    atlas_ingestion_ttl_hours: int = Field(default=168, ge=1)
    atlas_ingestion_max_retries: int = Field(default=3, ge=1, le=10)
    atlas_ingestion_max_bytes: int = Field(default=4_000_000, ge=1)
    atlas_agent_node_timeout_seconds: float = Field(default=15.0, gt=0)
    atlas_agent_checkpoint_ttl_hours: int = Field(default=24, ge=1)
    atlas_agent_review_ttl_hours: int = Field(default=24, ge=1)
    atlas_migration_head: str = "agent_checkpoint_claims"

    @field_validator(
        "openai_api_key",
        "atlas_visitor_hmac_secret",
        "atlas_operator_token",
        "langsmith_api_key",
        "langsmith_endpoint",
        "langsmith_workspace_id",
        mode="before",
    )
    @classmethod
    def blank_optional_langsmith_values(cls, value: object) -> object:
        """Treat empty values in local dotenv files as unset optional settings."""

        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def require_production_secrets(self) -> "Settings":
        """Fail closed when a production process starts without its required credentials."""

        if self.atlas_env != "production":
            return self

        required_secrets = {
            "OPENAI_API_KEY": self.openai_api_key,
            "ATLAS_VISITOR_HMAC_SECRET": self.atlas_visitor_hmac_secret,
            "ATLAS_OPERATOR_TOKEN": self.atlas_operator_token,
        }
        missing = [
            name
            for name, value in required_secrets.items()
            if value is None or not value.get_secret_value().strip()
        ]
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"Production configuration requires non-empty values for: {names}")

        if self.atlas_env in {"preview", "staging", "production"}:
            for name, origin in (("WEB_ORIGIN", self.web_origin), ("API_ORIGIN", self.api_origin)):
                if origin.scheme != "https":
                    raise ValueError(f"{name} must use HTTPS in {self.atlas_env}")
                host = origin.host or ""
                if "localhost" in host or host in {"127.0.0.1", "0.0.0.0"}:
                    raise ValueError(f"{name} cannot point to a local host in {self.atlas_env}")

        return self

    def safe_summary(self) -> SafeSettingsSummary:
        """Return only fields explicitly approved for content-free operational diagnostics."""

        return {
            "environment": self.atlas_env,
            "log_level": self.atlas_log_level,
            "answer_model": self.atlas_answer_model,
            "reasoning_effort": self.atlas_reasoning_effort,
            "embedding_model": self.atlas_embedding_model,
            "embedding_dimensions": self.atlas_embedding_dimensions,
            "anonymous_answer_limit": self.atlas_anonymous_answer_limit,
            "anonymous_comparison_limit": self.atlas_anonymous_comparison_limit,
            "anonymous_window_hours": self.atlas_anonymous_window_hours,
            "content_retention_days": self.atlas_content_retention_days,
            "web_origin": str(self.web_origin),
            "api_origin": str(self.api_origin),
        }


@lru_cache
def get_settings() -> Settings:
    """Return one immutable settings instance per process."""

    return Settings()
