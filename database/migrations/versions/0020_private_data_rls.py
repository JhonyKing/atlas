"""Enforce subject-based row-level security for identity and private data."""

from alembic import op
import sqlalchemy as sa


revision = "0020_private_data_rls"
down_revision = "0019_private_data"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE OR REPLACE FUNCTION atlas.current_subject_id()
            RETURNS uuid
            LANGUAGE plpgsql
            STABLE
            AS $$
            BEGIN
              RETURN NULLIF(current_setting('atlas.subject_id', true), '')::uuid;
            EXCEPTION WHEN invalid_text_representation THEN
              RETURN NULL;
            END
            $$;
            """
        )
    )
    for table in ("users", "sessions", "ownership_grants", "private_uploads", "deletion_jobs"):
        op.execute(sa.text(f"ALTER TABLE atlas.{table} ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE atlas.{table} FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text(
            """
            DROP POLICY IF EXISTS users_subject ON atlas.users;
            CREATE POLICY users_subject ON atlas.users FOR ALL TO atlas_api
              USING (id = atlas.current_subject_id())
              WITH CHECK (id = atlas.current_subject_id());
            DROP POLICY IF EXISTS sessions_subject ON atlas.sessions;
            CREATE POLICY sessions_subject ON atlas.sessions FOR ALL TO atlas_api
              USING (user_id = atlas.current_subject_id())
              WITH CHECK (user_id = atlas.current_subject_id());
            DROP POLICY IF EXISTS ownership_subject ON atlas.ownership_grants;
            CREATE POLICY ownership_subject ON atlas.ownership_grants FOR ALL TO atlas_api
              USING (user_id = atlas.current_subject_id())
              WITH CHECK (user_id = atlas.current_subject_id());
            DROP POLICY IF EXISTS uploads_subject ON atlas.private_uploads;
            CREATE POLICY uploads_subject ON atlas.private_uploads FOR ALL TO atlas_api
              USING (owner_id = atlas.current_subject_id())
              WITH CHECK (owner_id = atlas.current_subject_id());
            DROP POLICY IF EXISTS deletion_subject ON atlas.deletion_jobs;
            CREATE POLICY deletion_subject ON atlas.deletion_jobs FOR ALL TO atlas_api
              USING (requested_by = atlas.current_subject_id())
              WITH CHECK (requested_by = atlas.current_subject_id());
            DROP POLICY IF EXISTS private_worker_all ON atlas.private_uploads;
            CREATE POLICY private_worker_all ON atlas.private_uploads FOR ALL TO atlas_worker
              USING (true) WITH CHECK (true);
            DROP POLICY IF EXISTS deletion_worker_all ON atlas.deletion_jobs;
            CREATE POLICY deletion_worker_all ON atlas.deletion_jobs FOR ALL TO atlas_worker
              USING (true) WITH CHECK (true);
            """
        )
    )


def downgrade() -> None:
    for table in ("users", "sessions", "ownership_grants", "private_uploads", "deletion_jobs"):
        op.execute(sa.text(f"ALTER TABLE atlas.{table} DISABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS atlas.current_subject_id()"))
