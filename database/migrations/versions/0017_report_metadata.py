"""Record reproducibility metadata for report jobs."""

from alembic import op
import sqlalchemy as sa


revision = "0017_report_metadata"
down_revision = "0016_reports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.report_jobs
              ADD COLUMN IF NOT EXISTS model text NOT NULL DEFAULT 'gpt-5.6-luna',
              ADD COLUMN IF NOT EXISTS prompt_version text NOT NULL DEFAULT 'report-v1',
              ADD COLUMN IF NOT EXISTS corpus_snapshot text;
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.report_jobs
              DROP COLUMN IF EXISTS corpus_snapshot,
              DROP COLUMN IF EXISTS prompt_version,
              DROP COLUMN IF EXISTS model;
            """
        )
    )

