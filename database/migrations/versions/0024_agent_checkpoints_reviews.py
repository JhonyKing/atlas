"""Persist content-safe agent checkpoints and append-only review decisions."""

from alembic import op
import sqlalchemy as sa


revision = "0024_agent_checkpoints_reviews"
down_revision = "0023_policy_review_status"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.agent_checkpoints (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              thread_id uuid NOT NULL,
              state_version integer NOT NULL CHECK (state_version > 0),
              completed_node text NOT NULL,
              replay_key text NOT NULL,
              state_hash char(64) NOT NULL CHECK (state_hash ~ '^[0-9a-f]{64}$'),
              safe_summary jsonb NOT NULL,
              created_at timestamptz NOT NULL DEFAULT now(),
              expires_at timestamptz NOT NULL,
              UNIQUE (thread_id, replay_key)
            );
            CREATE TABLE IF NOT EXISTS atlas.agent_review_requests (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              run_id uuid NOT NULL,
              reviewer_id uuid REFERENCES atlas.users(id),
              evidence_ids text[] NOT NULL CHECK (cardinality(evidence_ids) > 0),
              proposed_hash char(64) NOT NULL CHECK (proposed_hash ~ '^[0-9a-f]{64}$'),
              status text NOT NULL CHECK (status IN ('pending','approved','edited','rejected')),
              expires_at timestamptz NOT NULL,
              created_at timestamptz NOT NULL DEFAULT now()
            );
            CREATE TABLE IF NOT EXISTS atlas.agent_review_decisions (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              request_id uuid NOT NULL REFERENCES atlas.agent_review_requests(id),
              reviewer_id uuid REFERENCES atlas.users(id),
              action text NOT NULL CHECK (action IN ('approve','edit','reject')),
              decision_key text NOT NULL UNIQUE,
              edited_hash char(64) CHECK (edited_hash IS NULL OR edited_hash ~ '^[0-9a-f]{64}$'),
              created_at timestamptz NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS agent_checkpoints_thread_idx
              ON atlas.agent_checkpoints(thread_id, created_at DESC);
            REVOKE ALL ON atlas.agent_checkpoints, atlas.agent_review_requests,
              atlas.agent_review_decisions FROM PUBLIC;
            GRANT SELECT, INSERT, UPDATE ON atlas.agent_checkpoints,
              atlas.agent_review_requests, atlas.agent_review_decisions TO atlas_worker;
            GRANT SELECT ON atlas.agent_checkpoints, atlas.agent_review_requests,
              atlas.agent_review_decisions TO atlas_readonly;
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DROP TABLE IF EXISTS atlas.agent_review_decisions;
            DROP TABLE IF EXISTS atlas.agent_review_requests;
            DROP TABLE IF EXISTS atlas.agent_checkpoints;
            """
        )
    )
