"""Add quarantined private uploads and durable deletion jobs."""

from alembic import op
import sqlalchemy as sa


revision = "0019_private_data"
down_revision = "0018_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.private_uploads (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              owner_id uuid NOT NULL REFERENCES atlas.users(id) ON DELETE CASCADE,
              storage_key text NOT NULL UNIQUE,
              declared_content_type text NOT NULL,
              detected_content_type text,
              size_bytes bigint NOT NULL CHECK (size_bytes > 0),
              content_hash char(64) CHECK (content_hash IS NULL OR content_hash ~ '^[0-9a-f]{64}$'),
              scan_status text NOT NULL CHECK (scan_status IN ('pending','clean','rejected','error')),
              parse_status text NOT NULL CHECK (parse_status IN ('pending','parsed','rejected','error')),
              retention_until timestamptz NOT NULL,
              created_at timestamptz NOT NULL DEFAULT now(),
              deleted_at timestamptz
            );
            CREATE INDEX IF NOT EXISTS private_uploads_owner_idx
              ON atlas.private_uploads(owner_id, created_at DESC);
            CREATE TABLE IF NOT EXISTS atlas.deletion_jobs (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              requested_by uuid NOT NULL REFERENCES atlas.users(id) ON DELETE CASCADE,
              scope text NOT NULL CHECK (scope IN ('account','upload','resource')),
              resource_id uuid,
              idempotency_key text NOT NULL CHECK (length(idempotency_key) BETWEEN 8 AND 128),
              status text NOT NULL CHECK (status IN ('accepted','running','completed','failed')),
              requested_at timestamptz NOT NULL DEFAULT now(),
              completed_at timestamptz,
              error_code text,
              UNIQUE (requested_by, idempotency_key)
            );
            REVOKE ALL ON atlas.private_uploads, atlas.deletion_jobs FROM PUBLIC;
            GRANT SELECT, INSERT, UPDATE, DELETE ON atlas.private_uploads, atlas.deletion_jobs TO atlas_api;
            GRANT SELECT, INSERT, UPDATE, DELETE ON atlas.private_uploads, atlas.deletion_jobs TO atlas_worker;
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.deletion_jobs"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.private_uploads"))
