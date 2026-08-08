"""Move pgvector out of public and close the Supabase RLS helper RPC."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0026_supabase_extension_security"
down_revision = "0025_supabase_security_hardening"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text("ALTER EXTENSION vector SET SCHEMA extensions"))
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
              IF to_regprocedure('public.rls_auto_enable()') IS NOT NULL THEN
                EXECUTE 'REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM anon, authenticated';
              END IF;
            END
            $$;
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("ALTER EXTENSION vector SET SCHEMA public"))
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
              IF to_regprocedure('public.rls_auto_enable()') IS NOT NULL THEN
                EXECUTE 'GRANT EXECUTE ON FUNCTION public.rls_auto_enable() TO anon, authenticated';
              END IF;
            END
            $$;
            """
        )
    )
