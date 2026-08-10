"""Provider-edge connection pooling for Supabase Postgres.

The rest of the application receives a standard psycopg connection from this adapter; no
Supabase SDK types or project identifiers leak into domain persistence ports.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from psycopg import Connection
from psycopg_pool import ConnectionPool


class SupabaseConnectionPool:
    """Small lifecycle wrapper around psycopg's transaction-aware pool."""

    def __init__(self, database_url: str, *, min_size: int = 1, max_size: int = 8) -> None:
        if "localhost" in database_url or "127.0.0.1" in database_url:
            raise ValueError("Supabase production pool cannot use a localhost database URL")
        self._pool = ConnectionPool(
            conninfo=database_url.replace("postgresql+psycopg://", "postgresql://", 1),
            min_size=min_size,
            max_size=max_size,
            open=False,
        )

    def open(self) -> None:
        self._pool.open(wait=True)

    def close(self) -> None:
        self._pool.close()

    @contextmanager
    def connection(self) -> Iterator[Connection[object]]:
        with self._pool.connection() as connection:
            yield connection
