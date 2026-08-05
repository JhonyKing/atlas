"""Persist evidence-backed technology comparison runs and matrices."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0012_comparisons"
down_revision = "0011_seed_collections"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.comparison_runs (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              request_id uuid NOT NULL,
              visitor_key_hash char(64) NOT NULL CHECK (visitor_key_hash ~ '^[0-9a-f]{64}$'),
              idempotency_key text NOT NULL CHECK (length(idempotency_key) BETWEEN 16 AND 128),
              corpus_snapshot_id uuid NOT NULL
                REFERENCES atlas.corpus_snapshots(id) ON DELETE RESTRICT,
              status text NOT NULL CHECK (
                status IN ('accepted', 'retrieving', 'normalizing', 'verifying',
                           'completed', 'abstained', 'cancelled', 'failed')
              ),
              created_at timestamptz NOT NULL DEFAULT now(),
              completed_at timestamptz,
              retained_until timestamptz NOT NULL,
              UNIQUE (visitor_key_hash, idempotency_key)
            );

            CREATE TABLE IF NOT EXISTS atlas.comparison_matrices (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              comparison_run_id uuid NOT NULL UNIQUE
                REFERENCES atlas.comparison_runs(id) ON DELETE CASCADE,
              technology_ids text[] NOT NULL CHECK (
                cardinality(technology_ids) BETWEEN 2 AND 4
              ),
              criterion_ids text[] NOT NULL CHECK (cardinality(criterion_ids) >= 1),
              result_hash char(64) CHECK (result_hash IS NULL OR result_hash ~ '^[0-9a-f]{64}$'),
              summary text CHECK (summary IS NULL OR length(summary) <= 2000),
              created_at timestamptz NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS atlas.comparison_cells (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              comparison_matrix_id uuid NOT NULL
                REFERENCES atlas.comparison_matrices(id) ON DELETE CASCADE,
              technology_id text NOT NULL CHECK (length(technology_id) BETWEEN 1 AND 64),
              criterion_id text NOT NULL CHECK (length(criterion_id) BETWEEN 1 AND 64),
              state text NOT NULL CHECK (
                state IN ('supported', 'unsupported', 'partial', 'contradictory')
              ),
              value text,
              unit text CHECK (unit IS NULL OR length(unit) <= 64),
              explanation text CHECK (explanation IS NULL OR length(explanation) <= 2000),
              observed_at timestamptz,
              UNIQUE (comparison_matrix_id, technology_id, criterion_id)
            );

            CREATE TABLE IF NOT EXISTS atlas.comparison_cell_evidence (
              comparison_cell_id uuid NOT NULL
                REFERENCES atlas.comparison_cells(id) ON DELETE CASCADE,
              chunk_id uuid NOT NULL REFERENCES atlas.chunks(id) ON DELETE RESTRICT,
              ordinal integer NOT NULL CHECK (ordinal > 0),
              created_at timestamptz NOT NULL DEFAULT now(),
              PRIMARY KEY (comparison_cell_id, chunk_id),
              UNIQUE (comparison_cell_id, ordinal)
            );

            CREATE TABLE IF NOT EXISTS atlas.comparison_run_tombstones (
              comparison_run_id uuid PRIMARY KEY,
              expired_at timestamptz NOT NULL,
              purged_at timestamptz NOT NULL,
              batch_key text NOT NULL
            );

            CREATE INDEX IF NOT EXISTS comparison_runs_visitor_created_idx
              ON atlas.comparison_runs(visitor_key_hash, created_at DESC);
            CREATE INDEX IF NOT EXISTS comparison_runs_expires_idx
              ON atlas.comparison_runs(retained_until);
            CREATE INDEX IF NOT EXISTS comparison_runs_status_idx
              ON atlas.comparison_runs(status, created_at DESC);

            REVOKE ALL ON atlas.comparison_runs, atlas.comparison_matrices,
              atlas.comparison_cells, atlas.comparison_cell_evidence,
              atlas.comparison_run_tombstones FROM PUBLIC;
            GRANT SELECT ON atlas.comparison_runs, atlas.comparison_matrices,
              atlas.comparison_cells, atlas.comparison_cell_evidence,
              atlas.comparison_run_tombstones TO atlas_readonly, atlas_api;
            GRANT SELECT, INSERT, UPDATE, DELETE ON atlas.comparison_runs,
              atlas.comparison_matrices, atlas.comparison_cells,
              atlas.comparison_cell_evidence, atlas.comparison_run_tombstones TO atlas_worker;
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DROP TABLE IF EXISTS atlas.comparison_run_tombstones;
            DROP TABLE IF EXISTS atlas.comparison_cell_evidence;
            DROP TABLE IF EXISTS atlas.comparison_cells;
            DROP TABLE IF EXISTS atlas.comparison_matrices;
            DROP TABLE IF EXISTS atlas.comparison_runs;
            """
        )
    )
