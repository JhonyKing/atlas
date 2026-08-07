"""T067 red tests for the bounded, idempotent anonymous-content purge."""

from __future__ import annotations

import os
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import psycopg
import pytest

from atlas.persistence.retention import PostgresRetentionRepository


def _database_url() -> str:
    return os.getenv(
        "ATLAS_DATABASE_URL",
        "postgresql://atlas:atlas-local-only@localhost:55432/atlas",
    ).replace("postgresql+psycopg://", "postgresql://", 1)


@pytest.fixture()
def connection() -> Generator[psycopg.Connection[tuple[Any, ...]]]:
    try:
        connection = psycopg.connect(_database_url())
    except psycopg.OperationalError as exc:
        pytest.skip(f"PostgreSQL is not available: {exc}")
    try:
        yield connection
    finally:
        connection.rollback()
        connection.close()


@pytest.mark.database
def test_purge_rolls_up_and_deletes_expired_content_in_idempotent_batches(
    connection: psycopg.Connection[tuple[Any, ...]],
) -> None:
    observed_at = datetime(2099, 8, 4, 12, 0, tzinfo=UTC)
    visitor_hash = "b" * 64
    key_prefix = f"python-retention-{uuid4().hex[:12]}-"
    expires_at = observed_at - timedelta(days=1)
    created_at = observed_at - timedelta(days=31)

    with connection.cursor() as cursor:
        for index, status, answer_status in (
            (1, "completed", "complete"),
            (2, "abstained", "abstained"),
            (3, "failed", None),
        ):
            cursor.execute(
                """
                INSERT INTO atlas.answer_runs(
                  visitor_key_hash, idempotency_key, question, status, answer_status,
                  model_provider, model_id, input_tokens, output_tokens, estimated_cost_usd,
                  latency_ms, created_at, expires_at
                ) VALUES (%s, %s, %s, %s, %s, 'openai', 'gpt-5.6-luna', %s, %s, %s, %s, %s, %s)
                """,
                (
                    visitor_hash,
                    f"{key_prefix}{index:03d}",
                    f"Question {index}",
                    status,
                    answer_status,
                    index * 10,
                    index * 5,
                    index / 100_000,
                    index * 100,
                    created_at,
                    expires_at,
                ),
            )

        first = PostgresRetentionRepository(connection).purge(now=observed_at, batch_size=2)
        assert first.purged_count == 2
        assert first.batch_key

        cursor.execute(
            "SELECT purged_count FROM atlas.purge_expired_interactions(%s, %s)",
            (observed_at, 2),
        )
        assert cursor.fetchone() == (1,)

        cursor.execute(
            "SELECT purged_count FROM atlas.purge_expired_interactions(%s, %s)",
            (observed_at, 2),
        )
        assert cursor.fetchone() == (0,)

        cursor.execute(
            """
            SELECT coalesce(sum(accepted_count), 0), coalesce(sum(input_tokens), 0),
                   coalesce(sum(output_tokens), 0), coalesce(sum(latency_sum_ms), 0)
            FROM atlas.daily_metrics
            WHERE metric_date = %s::date
            """,
            (created_at,),
        )
        assert cursor.fetchone() == (3, 60, 30, 600)

        cursor.execute(
            "SELECT count(*) FROM atlas.answer_runs WHERE idempotency_key LIKE %s",
            (f"{key_prefix}%",),
        )
        assert cursor.fetchone() == (0,)

        cursor.execute(
            "SELECT count(*) FROM atlas.answer_run_tombstones WHERE purged_at <= %s",
            (observed_at,),
        )
        assert cursor.fetchone() == (3,)

        cursor.execute(
            "DELETE FROM atlas.answer_run_tombstones WHERE purged_at = %s",
            (observed_at,),
        )
        cursor.execute(
            """
            DELETE FROM atlas.daily_metrics
            WHERE metric_date = %s AND dimension_key = 'gpt-5.6-luna'
            """,
            (created_at.date(),),
        )
        connection.commit()
