"""Persist explicit robots, terms, and license review status on collections."""

from alembic import op
import sqlalchemy as sa


revision = "0023_policy_review_status"
down_revision = "0022_ingestion_governance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.governed_collections
              ADD COLUMN IF NOT EXISTS robots_status text NOT NULL DEFAULT 'approved'
                CHECK (robots_status IN ('pending','approved','rejected')),
              ADD COLUMN IF NOT EXISTS terms_status text NOT NULL DEFAULT 'approved'
                CHECK (terms_status IN ('pending','approved','rejected')),
              ADD COLUMN IF NOT EXISTS license_status text NOT NULL DEFAULT 'approved'
                CHECK (license_status IN ('pending','approved','rejected'));
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE IF EXISTS atlas.governed_collections
              DROP COLUMN IF EXISTS robots_status,
              DROP COLUMN IF EXISTS terms_status,
              DROP COLUMN IF EXISTS license_status;
            """
        )
    )
