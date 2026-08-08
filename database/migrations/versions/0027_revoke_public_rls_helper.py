"""Prevent the hosted Supabase RLS helper from being exposed as a public RPC."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0027_revoke_public_rls_helper"
down_revision = "0026_supabase_extension_security"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
              IF to_regprocedure('public.rls_auto_enable()') IS NOT NULL THEN
                EXECUTE 'REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM PUBLIC';
              END IF;
            END
            $$;
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
              IF to_regprocedure('public.rls_auto_enable()') IS NOT NULL THEN
                EXECUTE 'GRANT EXECUTE ON FUNCTION public.rls_auto_enable() TO PUBLIC';
              END IF;
            END
            $$;
            """
        )
    )
