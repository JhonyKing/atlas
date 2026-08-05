from __future__ import annotations

import os

import psycopg
import pytest
from pydantic import SecretStr

from atlas.api.main import _verified_corpus_or_demo
from atlas.config import Settings
from atlas.persistence.corpus_status import PostgresCorpusStatusRepository


@pytest.mark.database
def test_runtime_uses_verified_postgres_snapshot_when_available() -> None:
    raw_dsn = os.getenv("ATLAS_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not raw_dsn:
        pytest.skip("ATLAS_DATABASE_URL is required for the PostgreSQL integration test")

    settings = Settings(database_url=SecretStr(raw_dsn))
    provider = _verified_corpus_or_demo(settings)

    assert isinstance(provider, PostgresCorpusStatusRepository)
    status = provider.get_status()
    assert status.snapshot_id
    assert {item.slug.value for item in status.collections} == {"langgraph", "langchain", "openai"}
    assert all(item.status.value == "ready" for item in status.collections)

    connection = provider._connection
    assert isinstance(connection, psycopg.Connection)
    connection.close()
