"""Add pricing evidence and an explicit not-applicable comparison state."""

from alembic import op
import sqlalchemy as sa


revision = "comparison_pricing_contract"
down_revision = "foreign_key_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.sources
              DROP CONSTRAINT IF EXISTS sources_source_type_check;
            ALTER TABLE atlas.sources
              ADD CONSTRAINT sources_source_type_check CHECK (
                source_type IN ('documentation', 'changelog', 'release_note', 'pricing')
              );

            ALTER TABLE atlas.comparison_cells
              DROP CONSTRAINT IF EXISTS comparison_cells_state_check;
            ALTER TABLE atlas.comparison_cells
              ADD CONSTRAINT comparison_cells_state_check CHECK (
                state IN ('supported', 'unsupported', 'not_applicable', 'partial', 'contradictory')
              );
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.comparison_cells
              DROP CONSTRAINT IF EXISTS comparison_cells_state_check;
            ALTER TABLE atlas.comparison_cells
              ADD CONSTRAINT comparison_cells_state_check CHECK (
                state IN ('supported', 'unsupported', 'partial', 'contradictory')
              );
            ALTER TABLE atlas.sources
              DROP CONSTRAINT IF EXISTS sources_source_type_check;
            ALTER TABLE atlas.sources
              ADD CONSTRAINT sources_source_type_check CHECK (
                source_type IN ('documentation', 'changelog', 'release_note')
              );
            """
        )
    )
