"""Persist comparison runs for report generation with visitor-scoped access."""

from alembic import op
import sqlalchemy as sa


revision = "comparison_run_persistence"
down_revision = "comparison_pricing_contract"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            GRANT INSERT, UPDATE ON atlas.comparison_runs TO atlas_api;
            GRANT INSERT ON atlas.comparison_matrices, atlas.comparison_cells,
              atlas.comparison_cell_evidence TO atlas_api;

            ALTER TABLE atlas.comparison_runs ENABLE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_runs FORCE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_matrices ENABLE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_matrices FORCE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_cells ENABLE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_cells FORCE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_cell_evidence ENABLE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_cell_evidence FORCE ROW LEVEL SECURITY;

            CREATE POLICY comparison_runs_api_owner ON atlas.comparison_runs
              FOR ALL TO atlas_api
              USING (visitor_key_hash = current_setting('atlas.visitor_key_hash', true))
              WITH CHECK (visitor_key_hash = current_setting('atlas.visitor_key_hash', true));
            CREATE POLICY comparison_runs_worker_all ON atlas.comparison_runs
              FOR ALL TO atlas_worker USING (true) WITH CHECK (true);
            CREATE POLICY comparison_runs_readonly_select ON atlas.comparison_runs
              FOR SELECT TO atlas_readonly USING (true);

            CREATE POLICY comparison_matrices_api_owner ON atlas.comparison_matrices
              FOR ALL TO atlas_api
              USING (EXISTS (
                SELECT 1 FROM atlas.comparison_runs r
                WHERE r.id = comparison_run_id
                  AND r.visitor_key_hash = current_setting('atlas.visitor_key_hash', true)
              ))
              WITH CHECK (EXISTS (
                SELECT 1 FROM atlas.comparison_runs r
                WHERE r.id = comparison_run_id
                  AND r.visitor_key_hash = current_setting('atlas.visitor_key_hash', true)
              ));
            CREATE POLICY comparison_matrices_worker_all ON atlas.comparison_matrices
              FOR ALL TO atlas_worker USING (true) WITH CHECK (true);
            CREATE POLICY comparison_matrices_readonly_select ON atlas.comparison_matrices
              FOR SELECT TO atlas_readonly USING (true);

            CREATE POLICY comparison_cells_api_owner ON atlas.comparison_cells
              FOR ALL TO atlas_api
              USING (EXISTS (
                SELECT 1 FROM atlas.comparison_matrices m
                JOIN atlas.comparison_runs r ON r.id = m.comparison_run_id
                WHERE m.id = comparison_matrix_id
                  AND r.visitor_key_hash = current_setting('atlas.visitor_key_hash', true)
              ))
              WITH CHECK (EXISTS (
                SELECT 1 FROM atlas.comparison_matrices m
                JOIN atlas.comparison_runs r ON r.id = m.comparison_run_id
                WHERE m.id = comparison_matrix_id
                  AND r.visitor_key_hash = current_setting('atlas.visitor_key_hash', true)
              ));
            CREATE POLICY comparison_cells_worker_all ON atlas.comparison_cells
              FOR ALL TO atlas_worker USING (true) WITH CHECK (true);
            CREATE POLICY comparison_cells_readonly_select ON atlas.comparison_cells
              FOR SELECT TO atlas_readonly USING (true);

            CREATE POLICY comparison_cell_evidence_api_owner ON atlas.comparison_cell_evidence
              FOR ALL TO atlas_api
              USING (EXISTS (
                SELECT 1
                FROM atlas.comparison_cells c
                JOIN atlas.comparison_matrices m ON m.id = c.comparison_matrix_id
                JOIN atlas.comparison_runs r ON r.id = m.comparison_run_id
                WHERE c.id = comparison_cell_id
                  AND r.visitor_key_hash = current_setting('atlas.visitor_key_hash', true)
              ))
              WITH CHECK (EXISTS (
                SELECT 1
                FROM atlas.comparison_cells c
                JOIN atlas.comparison_matrices m ON m.id = c.comparison_matrix_id
                JOIN atlas.comparison_runs r ON r.id = m.comparison_run_id
                WHERE c.id = comparison_cell_id
                  AND r.visitor_key_hash = current_setting('atlas.visitor_key_hash', true)
              ));
            CREATE POLICY comparison_cell_evidence_worker_all ON atlas.comparison_cell_evidence
              FOR ALL TO atlas_worker USING (true) WITH CHECK (true);
            CREATE POLICY comparison_cell_evidence_readonly_select ON atlas.comparison_cell_evidence
              FOR SELECT TO atlas_readonly USING (true);
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DROP POLICY IF EXISTS comparison_cell_evidence_readonly_select
              ON atlas.comparison_cell_evidence;
            DROP POLICY IF EXISTS comparison_cell_evidence_worker_all
              ON atlas.comparison_cell_evidence;
            DROP POLICY IF EXISTS comparison_cell_evidence_api_owner
              ON atlas.comparison_cell_evidence;
            DROP POLICY IF EXISTS comparison_cells_readonly_select ON atlas.comparison_cells;
            DROP POLICY IF EXISTS comparison_cells_worker_all ON atlas.comparison_cells;
            DROP POLICY IF EXISTS comparison_cells_api_owner ON atlas.comparison_cells;
            DROP POLICY IF EXISTS comparison_matrices_readonly_select
              ON atlas.comparison_matrices;
            DROP POLICY IF EXISTS comparison_matrices_worker_all ON atlas.comparison_matrices;
            DROP POLICY IF EXISTS comparison_matrices_api_owner ON atlas.comparison_matrices;
            DROP POLICY IF EXISTS comparison_runs_readonly_select ON atlas.comparison_runs;
            DROP POLICY IF EXISTS comparison_runs_worker_all ON atlas.comparison_runs;
            DROP POLICY IF EXISTS comparison_runs_api_owner ON atlas.comparison_runs;

            ALTER TABLE atlas.comparison_cell_evidence NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_cell_evidence DISABLE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_cells NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_cells DISABLE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_matrices NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_matrices DISABLE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_runs NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE atlas.comparison_runs DISABLE ROW LEVEL SECURITY;

            REVOKE INSERT, UPDATE ON atlas.comparison_runs FROM atlas_api;
            REVOKE INSERT ON atlas.comparison_matrices, atlas.comparison_cells,
              atlas.comparison_cell_evidence FROM atlas_api;
            """
        )
    )
