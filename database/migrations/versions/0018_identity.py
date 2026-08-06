"""Add authenticated users, sessions, and ownership grants."""

from alembic import op
import sqlalchemy as sa


revision = "0018_identity"
down_revision = "0017_report_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.users (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              auth_subject text NOT NULL UNIQUE,
              locale text NOT NULL DEFAULT 'en-US' CHECK (locale IN ('en-US','es-MX')),
              created_at timestamptz NOT NULL DEFAULT now(),
              deleted_at timestamptz
            );
            CREATE TABLE IF NOT EXISTS atlas.sessions (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              user_id uuid NOT NULL REFERENCES atlas.users(id) ON DELETE CASCADE,
              token_digest char(64) NOT NULL UNIQUE CHECK (token_digest ~ '^[0-9a-f]{64}$'),
              issued_at timestamptz NOT NULL,
              expires_at timestamptz NOT NULL,
              revoked_at timestamptz,
              last_seen_at timestamptz,
              device_label text CHECK (device_label IS NULL OR length(device_label) <= 120)
            );
            CREATE INDEX IF NOT EXISTS sessions_user_expiry_idx
              ON atlas.sessions(user_id, expires_at DESC);
            CREATE TABLE IF NOT EXISTS atlas.ownership_grants (
              user_id uuid NOT NULL REFERENCES atlas.users(id) ON DELETE CASCADE,
              resource_type text NOT NULL CHECK (
                resource_type IN ('thread','report','feedback','artifact','upload')
              ),
              resource_id uuid NOT NULL,
              created_at timestamptz NOT NULL DEFAULT now(),
              deleted_at timestamptz,
              PRIMARY KEY (user_id, resource_type, resource_id)
            );
            CREATE INDEX IF NOT EXISTS ownership_grants_resource_idx
              ON atlas.ownership_grants(resource_type, resource_id);
            REVOKE ALL ON atlas.users, atlas.sessions, atlas.ownership_grants FROM PUBLIC;
            GRANT SELECT, INSERT, UPDATE, DELETE ON atlas.users, atlas.sessions,
              atlas.ownership_grants TO atlas_api;
            GRANT SELECT, INSERT, UPDATE, DELETE ON atlas.users, atlas.sessions,
              atlas.ownership_grants TO atlas_worker;
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.ownership_grants"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.sessions"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.users"))
