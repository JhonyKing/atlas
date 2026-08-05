"""Executable configuration and secret-handling requirements."""

from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

from atlas.config import Settings


@pytest.fixture(autouse=True)
def isolate_settings_sources(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Prevent a developer's local environment file from influencing deterministic tests."""

    monkeypatch.chdir(tmp_path)
    for variable in (
        "ATLAS_ENV",
        "DATABASE_URL",
        "OPENAI_API_KEY",
        "ATLAS_VISITOR_HMAC_SECRET",
        "ATLAS_OPERATOR_TOKEN",
    ):
        monkeypatch.delenv(variable, raising=False)


def test_safe_defaults_select_the_approved_portfolio_baseline() -> None:
    settings = Settings()

    assert settings.atlas_env == "development"
    assert settings.atlas_answer_model == "gpt-5.6-luna"
    assert settings.atlas_reasoning_effort == "medium"
    assert settings.atlas_embedding_model == "text-embedding-3-small"
    assert settings.atlas_embedding_dimensions == 1536
    assert settings.atlas_anonymous_answer_limit == 10
    assert settings.atlas_anonymous_comparison_limit == 5
    assert settings.atlas_anonymous_window_hours == 24
    assert settings.atlas_content_retention_days == 30


def test_blank_optional_langsmith_values_are_treated_as_unset() -> None:
    settings = Settings(
        openai_api_key="",
        atlas_visitor_hmac_secret=" ",
        atlas_operator_token="",
        langsmith_api_key="",
        langsmith_endpoint="",
        langsmith_workspace_id="  ",
    )

    assert settings.openai_api_key is None
    assert settings.atlas_visitor_hmac_secret is None
    assert settings.atlas_operator_token is None
    assert settings.langsmith_api_key is None
    assert settings.langsmith_endpoint is None
    assert settings.langsmith_workspace_id is None


def test_production_rejects_missing_runtime_secrets() -> None:
    with pytest.raises(ValidationError, match="Production configuration requires"):
        Settings(atlas_env="production")


def test_safe_summary_contains_operations_data_but_no_secrets() -> None:
    raw_values = {
        "openai": "sk-test-openai-value",
        "visitor": "visitor-hmac-test-value",
        "operator": "operator-test-value",
        "database": "postgresql+psycopg://atlas:database-test-value@db:5432/atlas",
    }
    settings = Settings(
        database_url=SecretStr(raw_values["database"]),
        openai_api_key=SecretStr(raw_values["openai"]),
        atlas_visitor_hmac_secret=SecretStr(raw_values["visitor"]),
        atlas_operator_token=SecretStr(raw_values["operator"]),
    )

    summary = settings.safe_summary()
    rendered = repr(summary)

    assert summary["answer_model"] == "gpt-5.6-luna"
    assert summary["anonymous_answer_limit"] == 10
    assert "database_url" not in summary
    assert "openai_api_key" not in summary
    assert "atlas_visitor_hmac_secret" not in summary
    assert "atlas_operator_token" not in summary
    assert all(secret not in rendered for secret in raw_values.values())


def test_standard_representation_never_contains_raw_secret_values() -> None:
    secret = "sk-test-do-not-render"
    settings = Settings(openai_api_key=SecretStr(secret))

    assert secret not in repr(settings)
    assert secret not in str(settings)
