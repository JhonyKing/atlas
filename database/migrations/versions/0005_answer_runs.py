"""Persist answer-run state, evidence selections, claims, and citations."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0005_answer_runs"
down_revision = "0004_hybrid_retrieval"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.answer_runs (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              visitor_key_hash char(64) NOT NULL CHECK (visitor_key_hash ~ '^[0-9a-f]{64}$'),
              idempotency_key text NOT NULL CHECK (length(idempotency_key) BETWEEN 16 AND 128),
              corpus_snapshot_id uuid REFERENCES atlas.corpus_snapshots(id) ON DELETE RESTRICT,
              question text NOT NULL CHECK (length(question) BETWEEN 3 AND 2000),
              constraints jsonb NOT NULL DEFAULT '{}'::jsonb,
              status text NOT NULL CHECK (
                status IN ('accepted', 'retrieving', 'composing', 'verifying', 'completed',
                           'abstained', 'cancelling', 'cancelled', 'failed')
              ),
              answer_status text CHECK (answer_status IN ('complete', 'partial', 'abstained')),
              limitations jsonb NOT NULL DEFAULT '[]'::jsonb,
              model_provider text,
              model_id text,
              reasoning_effort text,
              prompt_version text,
              retrieval_version text,
              provider_response_id text,
              provider_request_id text,
              input_tokens integer CHECK (input_tokens IS NULL OR input_tokens >= 0),
              output_tokens integer CHECK (output_tokens IS NULL OR output_tokens >= 0),
              reasoning_tokens integer CHECK (reasoning_tokens IS NULL OR reasoning_tokens >= 0),
              cached_tokens integer CHECK (cached_tokens IS NULL OR cached_tokens >= 0),
              estimated_cost_usd numeric(12,6) CHECK (
                estimated_cost_usd IS NULL OR estimated_cost_usd >= 0
              ),
              price_table_version text,
              latency_ms integer CHECK (latency_ms IS NULL OR latency_ms >= 0),
              first_progress_ms integer CHECK (first_progress_ms IS NULL OR first_progress_ms >= 0),
              error_code text,
              created_at timestamptz NOT NULL DEFAULT now(),
              completed_at timestamptz,
              expires_at timestamptz NOT NULL,
              UNIQUE (visitor_key_hash, idempotency_key)
            );

            CREATE TABLE IF NOT EXISTS atlas.run_evidence (
              answer_run_id uuid NOT NULL REFERENCES atlas.answer_runs(id) ON DELETE CASCADE,
              chunk_id uuid NOT NULL REFERENCES atlas.chunks(id) ON DELETE RESTRICT,
              keyword_rank integer CHECK (keyword_rank IS NULL OR keyword_rank > 0),
              vector_rank integer CHECK (vector_rank IS NULL OR vector_rank > 0),
              fused_rank integer NOT NULL CHECK (fused_rank > 0),
              selected_for_context boolean NOT NULL DEFAULT false,
              created_at timestamptz NOT NULL DEFAULT now(),
              PRIMARY KEY (answer_run_id, chunk_id)
            );

            CREATE TABLE IF NOT EXISTS atlas.answer_claims (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              answer_run_id uuid NOT NULL REFERENCES atlas.answer_runs(id) ON DELETE CASCADE,
              ordinal integer NOT NULL CHECK (ordinal >= 0),
              text text NOT NULL CHECK (length(text) BETWEEN 1 AND 2000),
              claim_type text NOT NULL CHECK (claim_type IN ('factual', 'inference')),
              UNIQUE (answer_run_id, ordinal)
            );

            CREATE TABLE IF NOT EXISTS atlas.answer_citations (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              answer_run_id uuid NOT NULL REFERENCES atlas.answer_runs(id) ON DELETE CASCADE,
              claim_id uuid NOT NULL REFERENCES atlas.answer_claims(id) ON DELETE CASCADE,
              evidence_id uuid NOT NULL REFERENCES atlas.chunks(id) ON DELETE RESTRICT,
              UNIQUE (claim_id, evidence_id)
            );

            ALTER TABLE atlas.usage_events
              DROP CONSTRAINT IF EXISTS usage_events_answer_run_fk;
            ALTER TABLE atlas.usage_events
              ADD CONSTRAINT usage_events_answer_run_fk
              FOREIGN KEY (answer_run_id) REFERENCES atlas.answer_runs(id) ON DELETE CASCADE;

            CREATE INDEX IF NOT EXISTS answer_runs_visitor_created_idx
              ON atlas.answer_runs(visitor_key_hash, created_at DESC);
            CREATE INDEX IF NOT EXISTS answer_runs_status_idx
              ON atlas.answer_runs(status, created_at DESC);
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("ALTER TABLE atlas.usage_events DROP CONSTRAINT IF EXISTS usage_events_answer_run_fk"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.answer_citations"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.answer_claims"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.run_evidence"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.answer_runs"))
