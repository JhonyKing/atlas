"""Persist report artifacts across serverless instances with visitor-scoped RLS."""

import sqlalchemy as sa
from alembic import op

revision = "0035_durable_reports"
down_revision = "comparison_run_persistence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.report_documents ADD COLUMN IF NOT EXISTS content bytea;
            ALTER TABLE atlas.report_documents
              DROP CONSTRAINT IF EXISTS report_document_content_size;
            ALTER TABLE atlas.report_documents ADD CONSTRAINT report_document_content_size
              CHECK (content IS NULL OR (octet_length(content) = size_bytes
                                         AND size_bytes <= 2000000));

            GRANT INSERT, UPDATE ON atlas.report_jobs TO atlas_api;
            GRANT SELECT, INSERT, UPDATE, DELETE ON atlas.report_documents TO atlas_api;

            ALTER TABLE atlas.report_jobs ENABLE ROW LEVEL SECURITY;
            ALTER TABLE atlas.report_jobs FORCE ROW LEVEL SECURITY;
            ALTER TABLE atlas.report_documents ENABLE ROW LEVEL SECURITY;
            ALTER TABLE atlas.report_documents FORCE ROW LEVEL SECURITY;

            CREATE POLICY report_jobs_api_owner ON atlas.report_jobs
              FOR ALL TO atlas_api
              USING (visitor_key_hash = current_setting('atlas.visitor_key_hash', true))
              WITH CHECK (visitor_key_hash = current_setting('atlas.visitor_key_hash', true));
            CREATE POLICY report_jobs_worker_all ON atlas.report_jobs
              FOR ALL TO atlas_worker USING (true) WITH CHECK (true);
            CREATE POLICY report_jobs_readonly_select ON atlas.report_jobs
              FOR SELECT TO atlas_readonly USING (true);

            CREATE POLICY report_documents_api_owner ON atlas.report_documents
              FOR ALL TO atlas_api
              USING (EXISTS (
                SELECT 1 FROM atlas.report_jobs r
                WHERE r.id = report_job_id
                  AND r.visitor_key_hash = current_setting('atlas.visitor_key_hash', true)
              ))
              WITH CHECK (EXISTS (
                SELECT 1 FROM atlas.report_jobs r
                WHERE r.id = report_job_id
                  AND r.visitor_key_hash = current_setting('atlas.visitor_key_hash', true)
              ));
            CREATE POLICY report_documents_worker_all ON atlas.report_documents
              FOR ALL TO atlas_worker USING (true) WITH CHECK (true);
            CREATE POLICY report_documents_readonly_select ON atlas.report_documents
              FOR SELECT TO atlas_readonly USING (true);
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DROP POLICY IF EXISTS report_documents_readonly_select ON atlas.report_documents;
            DROP POLICY IF EXISTS report_documents_worker_all ON atlas.report_documents;
            DROP POLICY IF EXISTS report_documents_api_owner ON atlas.report_documents;
            DROP POLICY IF EXISTS report_jobs_readonly_select ON atlas.report_jobs;
            DROP POLICY IF EXISTS report_jobs_worker_all ON atlas.report_jobs;
            DROP POLICY IF EXISTS report_jobs_api_owner ON atlas.report_jobs;
            ALTER TABLE atlas.report_documents DISABLE ROW LEVEL SECURITY;
            ALTER TABLE atlas.report_jobs DISABLE ROW LEVEL SECURITY;
            REVOKE INSERT, UPDATE ON atlas.report_jobs FROM atlas_api;
            REVOKE SELECT, INSERT, UPDATE, DELETE ON atlas.report_documents FROM atlas_api;
            ALTER TABLE atlas.report_documents
              DROP CONSTRAINT IF EXISTS report_document_content_size;
            ALTER TABLE atlas.report_documents DROP COLUMN IF EXISTS content;
            """
        )
    )
