from __future__ import annotations

import os

import psycopg
import pytest
from pydantic import SecretStr

from atlas.api import main as main_module
from atlas.api.main import _verified_corpus_or_demo
from atlas.config import Settings
from atlas.persistence.corpus_status import PostgresCorpusStatusRepository


@pytest.mark.database
def test_runtime_uses_verified_postgres_snapshot_when_available() -> None:
    raw_dsn = os.getenv("ATLAS_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not raw_dsn:
        pytest.skip("ATLAS_DATABASE_URL is required for the PostgreSQL integration test")

    settings = Settings(
        atlas_env="production",
        database_url=SecretStr(raw_dsn),
        atlas_operator_token=SecretStr("integration-test-operator"),
        atlas_visitor_hmac_secret=SecretStr("integration-test-visitor-secret"),
    )
    provider = _verified_corpus_or_demo(settings)

    assert isinstance(provider, PostgresCorpusStatusRepository)
    status = provider.get_status()
    assert status.snapshot_id
    assert {item.slug.value for item in status.collections} == {
        "langgraph",
        "langchain",
        "openai",
        "anthropic",
        "gemini",
    }
    assert all(item.status.value == "ready" for item in status.collections)

    connection = provider._connection
    assert isinstance(connection, psycopg.Connection)
    connection.close()


@pytest.mark.database
def test_production_runtime_wires_the_verified_corpus_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_dsn = os.getenv("ATLAS_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not raw_dsn:
        pytest.skip("ATLAS_DATABASE_URL is required for the PostgreSQL integration test")

    settings = Settings(
        atlas_env="production",
        database_url=SecretStr(raw_dsn),
        atlas_operator_token=SecretStr("integration-test-operator"),
        atlas_visitor_hmac_secret=SecretStr("integration-test-visitor-secret"),
    )
    monkeypatch.setattr(main_module, "get_settings", lambda: settings)
    application = main_module.create_runtime_app()
    provider = application.state.corpus_service
    assert isinstance(provider, PostgresCorpusStatusRepository)
    assert provider.get_status().snapshot_id
    provider._connection.close()


@pytest.mark.database
def test_development_answer_traces_use_the_verified_snapshot_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_dsn = os.getenv("ATLAS_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not raw_dsn:
        pytest.skip("ATLAS_DATABASE_URL is required for the PostgreSQL integration test")

    settings = Settings(atlas_env="development", database_url=SecretStr(raw_dsn))
    monkeypatch.setattr(main_module, "get_settings", lambda: settings)
    application = main_module.create_runtime_app(use_real_provider=False)
    provider = application.state.corpus_service
    answer_service = application.state.answer_service

    assert isinstance(provider, PostgresCorpusStatusRepository)
    snapshot_id = str(provider.get_status().snapshot_id)
    assert answer_service._trace_metadata["corpus_snapshot"] == snapshot_id
    provider._connection.close()
