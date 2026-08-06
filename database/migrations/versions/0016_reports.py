"""Add evidence-backed report jobs and artifact metadata."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0016_reports"
down_revision = "0015_expand_corpus_collections"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.report_jobs (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              request_id uuid NOT NULL,
              visitor_key_hash char(64) NOT NULL CHECK (visitor_key_hash ~ '^[0-9a-f]{64}$'),
              source_run_id uuid NOT NULL REFERENCES atlas.comparison_runs(id),
              report_type text NOT NULL CHECK (report_type IN ('comparison','architecture_brief','adr','release_intelligence','research')),
              locale text NOT NULL CHECK (locale IN ('en-US','es-MX')),
              spec jsonb NOT NULL,
              status text NOT NULL CHECK (status IN ('accepted','planning','rendering','completed','failed','cancelled','expired','deleted')),
              idempotency_key text NOT NULL CHECK (length(idempotency_key) BETWEEN 16 AND 128),
              created_at timestamptz NOT NULL,
              completed_at timestamptz,
              expires_at timestamptz NOT NULL,
              error_code text,
              UNIQUE (visitor_key_hash, idempotency_key)
            );
            CREATE INDEX IF NOT EXISTS report_jobs_owner_created_idx
              ON atlas.report_jobs(visitor_key_hash, created_at DESC);
            CREATE TABLE IF NOT EXISTS atlas.report_documents (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              report_job_id uuid NOT NULL REFERENCES atlas.report_jobs(id) ON DELETE CASCADE,
              format text NOT NULL CHECK (format IN ('docx','pdf')),
              storage_key text NOT NULL,
              content_hash char(64) NOT NULL CHECK (content_hash ~ '^[0-9a-f]{64}$'),
              size_bytes bigint NOT NULL CHECK (size_bytes > 0),
              created_at timestamptz NOT NULL,
              expires_at timestamptz NOT NULL,
              UNIQUE (report_job_id, format)
            );
            REVOKE ALL ON atlas.report_jobs, atlas.report_documents FROM PUBLIC;
            GRANT SELECT, INSERT, UPDATE ON atlas.report_jobs, atlas.report_documents TO atlas_worker;
            GRANT SELECT ON atlas.report_jobs, atlas.report_documents TO atlas_readonly, atlas_api;
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.report_documents"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.report_jobs"))

