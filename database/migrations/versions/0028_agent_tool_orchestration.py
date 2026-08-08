"""Persist bounded agent plans, runs, tool calls, approvals, and lifecycle events."""

from alembic import op
import sqlalchemy as sa


revision = "0028_agent_tool_orchestration"
down_revision = "0027_revoke_public_rls_helper"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.agent_plans (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              run_id uuid NOT NULL UNIQUE,
              plan_hash char(64) NOT NULL UNIQUE CHECK (plan_hash ~ '^[0-9a-f]{64}$'),
              request text NOT NULL CHECK (char_length(request) BETWEEN 1 AND 4000),
              locale text NOT NULL CHECK (locale IN ('en-US', 'es-MX')),
              model_label text NOT NULL,
              steps jsonb NOT NULL,
              risk_summary jsonb NOT NULL DEFAULT '[]'::jsonb,
              budget jsonb NOT NULL,
              expires_at timestamptz NOT NULL,
              created_at timestamptz NOT NULL DEFAULT now()
            );
            CREATE TABLE IF NOT EXISTS atlas.agent_runs (
              id uuid PRIMARY KEY,
              plan_id uuid NOT NULL REFERENCES atlas.agent_plans(id),
              actor_id text NOT NULL,
              status text NOT NULL CHECK (status IN (
                'accepted','planned','running','awaiting_approval','completed',
                'abstained','cancelled','failed','rejected'
              )),
              output jsonb NOT NULL DEFAULT '{}'::jsonb,
              created_at timestamptz NOT NULL DEFAULT now(),
              updated_at timestamptz NOT NULL DEFAULT now()
            );
            CREATE TABLE IF NOT EXISTS atlas.agent_tool_calls (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              run_id uuid NOT NULL REFERENCES atlas.agent_runs(id) ON DELETE CASCADE,
              call_id text NOT NULL,
              tool_id text NOT NULL,
              tool_version text NOT NULL,
              arguments_hash char(64) NOT NULL CHECK (arguments_hash ~ '^[0-9a-f]{64}$'),
              status text NOT NULL,
              evidence_ids text[] NOT NULL DEFAULT '{}',
              artifact_ids text[] NOT NULL DEFAULT '{}',
              error_category text,
              started_at timestamptz,
              completed_at timestamptz,
              UNIQUE (run_id, call_id)
            );
            CREATE TABLE IF NOT EXISTS atlas.agent_run_events (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              run_id uuid NOT NULL REFERENCES atlas.agent_runs(id) ON DELETE CASCADE,
              sequence integer NOT NULL CHECK (sequence > 0),
              event_type text NOT NULL,
              status text NOT NULL,
              call_id text,
              tool_id text,
              tool_version text,
              evidence_ids text[] NOT NULL DEFAULT '{}',
              artifact_ids text[] NOT NULL DEFAULT '{}',
              error_category text,
              correlation_id uuid NOT NULL DEFAULT atlas.new_uuid(),
              trace_id text,
              occurred_at timestamptz NOT NULL DEFAULT now(),
              UNIQUE (run_id, sequence)
            );
            CREATE TABLE IF NOT EXISTS atlas.agent_approvals (
              approval_id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              run_id uuid NOT NULL REFERENCES atlas.agent_runs(id) ON DELETE CASCADE,
              call_id text NOT NULL,
              actor_id text NOT NULL,
              tool_id text NOT NULL,
              tool_version text NOT NULL,
              arguments_hash char(64) NOT NULL CHECK (arguments_hash ~ '^[0-9a-f]{64}$'),
              target_resource text NOT NULL,
              decision text NOT NULL CHECK (decision IN ('approved','rejected','expired')),
              decision_key text NOT NULL UNIQUE,
              expires_at timestamptz NOT NULL,
              created_at timestamptz NOT NULL DEFAULT now(),
              UNIQUE (run_id, call_id)
            );
            CREATE INDEX IF NOT EXISTS agent_runs_status_idx
              ON atlas.agent_runs(status, created_at DESC);
            CREATE INDEX IF NOT EXISTS agent_run_events_run_idx
              ON atlas.agent_run_events(run_id, sequence);
            CREATE INDEX IF NOT EXISTS agent_tool_calls_run_idx
              ON atlas.agent_tool_calls(run_id, call_id);
            REVOKE ALL ON atlas.agent_plans, atlas.agent_runs, atlas.agent_tool_calls,
              atlas.agent_run_events, atlas.agent_approvals FROM PUBLIC;
            GRANT SELECT ON atlas.agent_plans, atlas.agent_runs, atlas.agent_tool_calls,
              atlas.agent_run_events, atlas.agent_approvals TO atlas_readonly;
            GRANT SELECT, INSERT, UPDATE ON atlas.agent_plans, atlas.agent_runs,
              atlas.agent_tool_calls, atlas.agent_run_events, atlas.agent_approvals TO atlas_worker;
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DROP TABLE IF EXISTS atlas.agent_approvals;
            DROP TABLE IF EXISTS atlas.agent_run_events;
            DROP TABLE IF EXISTS atlas.agent_tool_calls;
            DROP TABLE IF EXISTS atlas.agent_runs;
            DROP TABLE IF EXISTS atlas.agent_plans;
            """
        )
    )
