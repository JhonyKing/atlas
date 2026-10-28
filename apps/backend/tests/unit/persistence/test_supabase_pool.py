"""Supabase pool adapter boundaries."""

from typing import Any, cast

import psycopg
import pytest
from psycopg import Connection

from atlas.persistence.supabase import SupabaseConnectionPool, connect_supabase


def test_supabase_pool_rejects_local_database_fallback() -> None:
    with pytest.raises(ValueError, match="localhost"):
        SupabaseConnectionPool("postgresql+psycopg://atlas:secret@localhost:5432/atlas")


def test_supabase_pool_keeps_provider_edge_types_internal() -> None:
    pool = SupabaseConnectionPool("postgresql+psycopg://atlas:secret@db.example:5432/atlas")
    assert pool._pool.max_size == 8
    pool.close()


def test_supabase_connections_disable_server_side_preparation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, Any] = {}

    def connect(conninfo: str, **kwargs: Any) -> Connection[tuple[Any, ...]]:
        calls["conninfo"] = conninfo
        calls.update(kwargs)
        return cast(Connection[tuple[Any, ...]], object())

    monkeypatch.setattr(psycopg, "connect", connect)

    connect_supabase("postgresql+psycopg://atlas:secret@db.example:5432/atlas")

    assert calls == {
        "conninfo": "postgresql://atlas:secret@db.example:5432/atlas",
        "prepare_threshold": None,
    }


def test_supabase_pool_disables_server_side_preparation(monkeypatch: pytest.MonkeyPatch) -> None:
    pool_options: dict[str, Any] = {}

    class PoolStub:
        def __init__(self, **kwargs: Any) -> None:
            pool_options.update(kwargs)

    monkeypatch.setattr("atlas.persistence.supabase.ConnectionPool", PoolStub)

    SupabaseConnectionPool("postgresql://atlas:secret@db.example:5432/atlas")

    assert pool_options["kwargs"] == {"prepare_threshold": None}
