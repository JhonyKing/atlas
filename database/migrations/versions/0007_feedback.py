"""Persist one replaceable feedback record per retained anonymous answer."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0007_feedback"
down_revision = "0006_evidence_integrity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.feedback (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              answer_run_id uuid NOT NULL REFERENCES atlas.answer_runs(id) ON DELETE CASCADE,
              visitor_key_hash char(64) NOT NULL CHECK (visitor_key_hash ~ '^[0-9a-f]{64}$'),
              label text NOT NULL CHECK (label IN ('useful', 'not_useful')),
              category text CHECK (
                category IS NULL OR category IN (
                  'incorrect_citation', 'incorrect_answer', 'outdated', 'incomplete', 'other'
                )
              ),
              comment text CHECK (comment IS NULL OR length(comment) <= 1000),
              created_at timestamptz NOT NULL DEFAULT now(),
              expires_at timestamptz NOT NULL,
              UNIQUE (answer_run_id, visitor_key_hash)
            );

            CREATE INDEX IF NOT EXISTS feedback_expires_idx
              ON atlas.feedback(expires_at);
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.feedback"))
