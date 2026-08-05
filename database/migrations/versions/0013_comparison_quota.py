"""Add a separate rolling quota for anonymous comparisons."""

from __future__ import annotations

from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "0013_comparison_quota"
down_revision = "0012_comparisons"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.comparison_usage_events (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              visitor_key_hash char(64) NOT NULL CHECK (visitor_key_hash ~ '^[0-9a-f]{64}$'),
              idempotency_key text NOT NULL CHECK (length(idempotency_key) BETWEEN 16 AND 128),
              comparison_run_id uuid NOT NULL,
              accepted_at timestamptz NOT NULL,
              expires_at timestamptz NOT NULL,
              remaining_after integer NOT NULL CHECK (remaining_after BETWEEN 0 AND 4),
              UNIQUE (visitor_key_hash, idempotency_key),
              UNIQUE (comparison_run_id)
            );
            CREATE INDEX IF NOT EXISTS comparison_usage_visitor_accepted_idx
              ON atlas.comparison_usage_events(visitor_key_hash, accepted_at);
            REVOKE ALL ON atlas.comparison_usage_events FROM PUBLIC;
            GRANT SELECT ON atlas.comparison_usage_events TO atlas_readonly, atlas_api;
            GRANT SELECT, INSERT, UPDATE ON atlas.comparison_usage_events TO atlas_worker;
            """
        )
    )
    function_path = (
        Path(__file__).resolve().parents[2]
        / "functions"
        / "reserve_comparison_quota.sql"
    )
    op.execute(sa.text(function_path.read_text(encoding="utf-8")))


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP FUNCTION IF EXISTS atlas.reserve_comparison_quota(text, text, uuid, timestamptz)"
        )
    )
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.comparison_usage_events"))
