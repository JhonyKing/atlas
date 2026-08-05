"""PostgreSQL feedback persistence with retention and replacement semantics."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from uuid import UUID

from psycopg import Connection

from atlas.api.routes.feedback import FeedbackExpired, FeedbackNotFound


class PostgresFeedbackRepository:
    """Store one replaceable feedback record per visitor and retained answer."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def put(
        self,
        run_id: UUID,
        *,
        visitor_key_hash: str,
        feedback: Mapping[str, object],
    ) -> None:
        now = datetime.now(UTC)
        row = self._connection.execute(
            "SELECT expires_at FROM atlas.answer_runs WHERE id = %s",
            (run_id,),
        ).fetchone()
        if row is None:
            raise FeedbackNotFound(run_id)
        if row[0] <= now:
            raise FeedbackExpired(run_id)

        category = feedback.get("category")
        comment = feedback.get("comment")
        self._connection.execute(
            """
            INSERT INTO atlas.feedback(
              answer_run_id, visitor_key_hash, label, category, comment, expires_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (answer_run_id, visitor_key_hash)
            DO UPDATE SET
              label = EXCLUDED.label,
              category = EXCLUDED.category,
              comment = EXCLUDED.comment,
              created_at = now(),
              expires_at = EXCLUDED.expires_at
            """,
            (
                run_id,
                visitor_key_hash,
                str(feedback["label"]),
                str(category) if category is not None else None,
                str(comment) if comment is not None else None,
                row[0],
            ),
        )
        self._connection.commit()
