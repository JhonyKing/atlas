"""Preserve period and version context for normalized comparison cells."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0014_comparison_cell_context"
down_revision = "0013_comparison_quota"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.comparison_cells
              ADD COLUMN IF NOT EXISTS period text
                CHECK (period IS NULL OR length(period) BETWEEN 1 AND 64),
              ADD COLUMN IF NOT EXISTS version text
                CHECK (version IS NULL OR length(version) BETWEEN 1 AND 64);
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.comparison_cells
              DROP COLUMN IF EXISTS version,
              DROP COLUMN IF EXISTS period;
            """
        )
    )
