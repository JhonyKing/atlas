"""Add page, language and OCR provenance to source versions and chunks."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0009_provenance"
down_revision = "0008_retention"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.source_versions
              ADD COLUMN IF NOT EXISTS page_count integer NOT NULL DEFAULT 1
                CHECK (page_count > 0),
              ADD COLUMN IF NOT EXISTS language text NOT NULL DEFAULT 'unknown',
              ADD COLUMN IF NOT EXISTS ocr_used boolean NOT NULL DEFAULT false,
              ADD COLUMN IF NOT EXISTS ocr_confidence numeric(4,3)
                CHECK (ocr_confidence IS NULL OR (ocr_confidence >= 0 AND ocr_confidence <= 1));

            ALTER TABLE atlas.chunks
              ADD COLUMN IF NOT EXISTS page_start integer NOT NULL DEFAULT 1
                CHECK (page_start > 0),
              ADD COLUMN IF NOT EXISTS page_end integer NOT NULL DEFAULT 1
                CHECK (page_end >= page_start),
              ADD COLUMN IF NOT EXISTS language text NOT NULL DEFAULT 'unknown',
              ADD COLUMN IF NOT EXISTS ocr_used boolean NOT NULL DEFAULT false,
              ADD COLUMN IF NOT EXISTS ocr_confidence numeric(4,3)
                CHECK (ocr_confidence IS NULL OR (ocr_confidence >= 0 AND ocr_confidence <= 1));
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.chunks
              DROP COLUMN IF EXISTS ocr_confidence,
              DROP COLUMN IF EXISTS ocr_used,
              DROP COLUMN IF EXISTS language,
              DROP COLUMN IF EXISTS page_end,
              DROP COLUMN IF EXISTS page_start;
            ALTER TABLE atlas.source_versions
              DROP COLUMN IF EXISTS ocr_confidence,
              DROP COLUMN IF EXISTS ocr_used,
              DROP COLUMN IF EXISTS language,
              DROP COLUMN IF EXISTS page_count;
            """
        )
    )
