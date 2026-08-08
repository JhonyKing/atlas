"""Harden ATLAS function search paths for hosted Supabase execution."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0025_supabase_security_hardening"
down_revision = "0024_agent_checkpoints_reviews"
branch_labels = None
depends_on = None


_FUNCTIONS = (
    ("current_subject_id", ""),
    ("enqueue_ingestion", "uuid, text, text, text"),
    ("fail_ingestion_run", "uuid, text, integer"),
    ("get_answer_result", "uuid"),
    ("new_uuid", ""),
    ("promote_source_version", "uuid, uuid"),
    ("purge_expired_interactions", "timestamptz, integer"),
    ("reserve_answer_quota", "text, text, uuid, timestamptz"),
    ("reserve_comparison_quota", "text, text, uuid, timestamptz"),
    ("search_evidence", "text, text, vector, integer, uuid"),
    ("touch_updated_at", ""),
)


def upgrade() -> None:
    for name, arguments in _FUNCTIONS:
        op.execute(
            sa.text(
                f"ALTER FUNCTION atlas.{name}({arguments}) "
                "SET search_path = pg_catalog, atlas, extensions, public"
            )
        )


def downgrade() -> None:
    for name, arguments in _FUNCTIONS:
        op.execute(sa.text(f"ALTER FUNCTION atlas.{name}({arguments}) RESET search_path"))
