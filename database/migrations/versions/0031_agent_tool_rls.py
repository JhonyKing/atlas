"""Enable explicit RLS policies for durable agent orchestration records."""

from alembic import op
import sqlalchemy as sa


revision = "agent_tool_rls"
down_revision = "agent_checkpoint_claims"
branch_labels = None
depends_on = None

_TABLES = (
    "agent_plans",
    "agent_runs",
    "agent_tool_calls",
    "agent_run_events",
    "agent_approvals",
    "agent_idempotency_records",
    "agent_checkpoint_claims",
)


def upgrade() -> None:
    for table in _TABLES:
        op.execute(sa.text(f"ALTER TABLE atlas.{table} ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE atlas.{table} FORCE ROW LEVEL SECURITY"))
        op.execute(
            sa.text(
                f"""
                DROP POLICY IF EXISTS {table}_worker_all ON atlas.{table};
                CREATE POLICY {table}_worker_all ON atlas.{table} FOR ALL TO atlas_worker
                  USING (true) WITH CHECK (true);
                DROP POLICY IF EXISTS {table}_readonly_select ON atlas.{table};
                CREATE POLICY {table}_readonly_select ON atlas.{table} FOR SELECT TO atlas_readonly
                  USING (true);
                """
            )
        )


def downgrade() -> None:
    for table in _TABLES:
        op.execute(
            sa.text(
                f"DROP POLICY IF EXISTS {table}_worker_all ON atlas.{table};"
                f" DROP POLICY IF EXISTS {table}_readonly_select ON atlas.{table};"
                f" ALTER TABLE atlas.{table} NO FORCE ROW LEVEL SECURITY;"
                f" ALTER TABLE atlas.{table} DISABLE ROW LEVEL SECURITY;"
            )
        )
