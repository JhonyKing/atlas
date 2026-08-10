"""Persist one-shot checkpoint replay claims across worker processes."""

from alembic import op
import sqlalchemy as sa


revision = "agent_checkpoint_claims"
down_revision = "agent_idempotency"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.agent_checkpoint_claims (
              claim_token uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              thread_id uuid NOT NULL,
              replay_key text NOT NULL CHECK (char_length(replay_key) BETWEEN 1 AND 128),
              checkpoint_id uuid NOT NULL REFERENCES atlas.agent_checkpoints(id) ON DELETE CASCADE,
              claimed_at timestamptz NOT NULL DEFAULT now(),
              UNIQUE (thread_id, replay_key)
            );
            CREATE INDEX IF NOT EXISTS agent_checkpoint_claims_checkpoint_idx
              ON atlas.agent_checkpoint_claims(checkpoint_id);
            REVOKE ALL ON atlas.agent_checkpoint_claims FROM PUBLIC;
            GRANT SELECT, INSERT ON atlas.agent_checkpoint_claims TO atlas_worker;
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.agent_checkpoint_claims"))
