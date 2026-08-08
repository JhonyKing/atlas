"""Supabase pool adapter boundaries."""

import pytest

from atlas.persistence.supabase import SupabaseConnectionPool


def test_supabase_pool_rejects_local_database_fallback() -> None:
    with pytest.raises(ValueError, match="localhost"):
        SupabaseConnectionPool("postgresql+psycopg://atlas:secret@localhost:5432/atlas")


def test_supabase_pool_keeps_provider_edge_types_internal() -> None:
    pool = SupabaseConnectionPool("postgresql+psycopg://atlas:secret@db.example:5432/atlas")
    assert pool._pool.max_size == 8
    pool.close()
