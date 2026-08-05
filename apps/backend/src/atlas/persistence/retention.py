"""Bounded PostgreSQL retention orchestration for anonymous interaction content."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from psycopg import Connection


@dataclass(frozen=True, slots=True)
class RetentionBatchResult:
    """Content-free result of one retention batch."""

    purged_count: int
    batch_key: str
    remaining_expired_count: int


class PostgresRetentionRepository:
    """Call the transactional purge function and commit one bounded batch."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def purge(
        self,
        *,
        now: datetime | None = None,
        batch_size: int = 100,
    ) -> RetentionBatchResult:
        observed_at = now.astimezone(UTC) if now is not None else datetime.now(UTC)
        row = self._connection.execute(
            """
            SELECT purged_count, batch_key, remaining_expired_count
            FROM atlas.purge_expired_interactions(%s, %s)
            """,
            (observed_at, batch_size),
        ).fetchone()
        if row is None:
            raise RuntimeError("retention function returned no result")
        self._connection.commit()
        return RetentionBatchResult(
            purged_count=int(row[0]),
            batch_key=str(row[1]),
            remaining_expired_count=int(row[2]),
        )
