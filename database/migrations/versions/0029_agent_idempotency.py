"""Persist agent request fingerprints and bounded replay responses."""

from alembic import op
import sqlalchemy as sa


revision = "0029_agent_idempotency"
down_revision = "0028_agent_tool_orchestration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.agent_idempotency_records (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              scope text NOT NULL CHECK (char_length(scope) BETWEEN 1 AND 64),
              idempotency_key text NOT NULL CHECK (char_length(idempotency_key) BETWEEN 8 AND 128),
              fingerprint char(64) NOT NULL CHECK (fingerprint ~ '^[0-9a-f]{64}$'),
              response jsonb NOT NULL,
              created_at timestamptz NOT NULL DEFAULT now(),
              UNIQUE (scope, idempotency_key)
            );
            CREATE INDEX IF NOT EXISTS agent_idempotency_created_idx
              ON atlas.agent_idempotency_records(created_at);
            REVOKE ALL ON atlas.agent_idempotency_records FROM PUBLIC;
            GRANT SELECT, INSERT, UPDATE ON atlas.agent_idempotency_records TO atlas_worker;
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.agent_idempotency_records"))
