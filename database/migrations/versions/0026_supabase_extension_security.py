"""Move pgvector out of public and close the Supabase RLS helper RPC."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0026_supabase_extension_security"
down_revision = "0025_supabase_security_hardening"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Supabase creates this schema for managed extensions, while the local
    # pgvector image starts with the extension in ``public`` and no
    # ``extensions`` schema. Keep the migration self-contained so the same
    # Alembic chain works against both environments.
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS extensions"))
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
