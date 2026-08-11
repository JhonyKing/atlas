"""Deployment environment boundary contracts."""

import pytest
from pydantic import AnyHttpUrl, SecretStr

from atlas.config import Settings


def test_production_rejects_localhost_origins() -> None:
    with pytest.raises(ValueError, match=r"HTTPS|local host"):
        Settings(
            atlas_env="production",
            web_origin=AnyHttpUrl("http://localhost:3000"),
            api_origin=AnyHttpUrl("http://localhost:8000"),
            openai_api_key=SecretStr("test-key"),
            atlas_visitor_hmac_secret=SecretStr("visitor-secret"),
            atlas_operator_token=SecretStr("operator-token"),
        )


def test_production_rejects_missing_required_secrets() -> None:
    with pytest.raises(ValueError, match="Production configuration requires"):
        Settings(
            atlas_env="production",
            web_origin=AnyHttpUrl("https://atlas.example"),
            api_origin=AnyHttpUrl("https://api.atlas.example"),
        )


def test_safe_summary_never_contains_secret_values() -> None:
    settings = Settings(openai_api_key=SecretStr("sk-test-not-exported"))
    summary = settings.safe_summary()
    assert "sk-test-not-exported" not in repr(summary)


def test_managed_database_secret_name_is_consumed(monkeypatch: pytest.MonkeyPatch) -> None:
    managed_dsn = "postgresql+psycopg://atlas:managed-test@pooler.example:6543/atlas"
    monkeypatch.setenv("ATLAS_DATABASE_URL", managed_dsn)

    assert Settings().database_url.get_secret_value() == managed_dsn
