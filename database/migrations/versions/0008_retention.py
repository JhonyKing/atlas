"""Add content-free retention aggregates, tombstones, and daily scheduling metadata."""

from __future__ import annotations

from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "0008_retention"
down_revision = "0007_feedback"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.daily_metrics (
              metric_date date NOT NULL,
              dimension_key text NOT NULL CHECK (length(dimension_key) BETWEEN 1 AND 64),
              accepted_count bigint NOT NULL DEFAULT 0 CHECK (accepted_count >= 0),
              completed_count bigint NOT NULL DEFAULT 0 CHECK (completed_count >= 0),
              abstained_count bigint NOT NULL DEFAULT 0 CHECK (abstained_count >= 0),
              error_count bigint NOT NULL DEFAULT 0 CHECK (error_count >= 0),
              quota_denied_count bigint NOT NULL DEFAULT 0 CHECK (quota_denied_count >= 0),
              useful_count bigint NOT NULL DEFAULT 0 CHECK (useful_count >= 0),
              citation_count bigint NOT NULL DEFAULT 0 CHECK (citation_count >= 0),
              input_tokens bigint NOT NULL DEFAULT 0 CHECK (input_tokens >= 0),
              output_tokens bigint NOT NULL DEFAULT 0 CHECK (output_tokens >= 0),
              estimated_cost_usd numeric(14,6) NOT NULL DEFAULT 0 CHECK (estimated_cost_usd >= 0),
              latency_sum_ms bigint NOT NULL DEFAULT 0 CHECK (latency_sum_ms >= 0),
              latency_sample_count bigint NOT NULL DEFAULT 0 CHECK (latency_sample_count >= 0),
              PRIMARY KEY (metric_date, dimension_key)
            );

            CREATE TABLE IF NOT EXISTS atlas.answer_run_tombstones (
              answer_run_id uuid PRIMARY KEY,
              expired_at timestamptz NOT NULL,
              purged_at timestamptz NOT NULL,
              batch_key text NOT NULL
            );
            CREATE INDEX IF NOT EXISTS answer_run_tombstones_purged_idx
              ON atlas.answer_run_tombstones(purged_at);

            CREATE TABLE IF NOT EXISTS atlas.retention_jobs (
              name text PRIMARY KEY,
              cron_expression text NOT NULL CHECK (cron_expression = '0 2 * * *'),
              status text NOT NULL DEFAULT 'enabled' CHECK (status IN ('enabled', 'disabled')),
              last_run_at timestamptz,
              created_at timestamptz NOT NULL DEFAULT now()
            );
            INSERT INTO atlas.retention_jobs(name, cron_expression, status)
            VALUES ('interaction_retention', '0 2 * * *', 'enabled')
            ON CONFLICT (name) DO NOTHING;
            """
        )
    )

    function_path = Path(__file__).resolve().parents[2] / "functions" / "purge_expired_interactions.sql"
    op.execute(sa.text(function_path.read_text(encoding="utf-8")))


def downgrade() -> None:
    op.execute(sa.text("DROP FUNCTION IF EXISTS atlas.purge_expired_interactions(timestamptz, integer)"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.retention_jobs"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.answer_run_tombstones"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.daily_metrics"))
