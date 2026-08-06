"""Record private-upload provenance metadata."""

from alembic import op
import sqlalchemy as sa


revision = "0021_private_upload_provenance"
down_revision = "0020_private_data_rls"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "private_uploads",
        sa.Column("provenance", sa.Text(), nullable=False, server_default="private_upload"),
        schema="atlas",
    )


def downgrade() -> None:
    op.drop_column("private_uploads", "provenance", schema="atlas")
