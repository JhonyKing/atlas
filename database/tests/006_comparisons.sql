-- T006: comparison persistence, evidence, snapshot, retention, and idempotency contracts.
\set ON_ERROR_STOP on

DO $$
DECLARE table_name text;
BEGIN
  FOREACH table_name IN ARRAY ARRAY[
    'comparison_runs', 'comparison_matrices', 'comparison_cells',
    'comparison_cell_evidence', 'comparison_run_tombstones'
  ] LOOP
    IF to_regclass('atlas.' || table_name) IS NULL THEN
      RAISE EXCEPTION 'atlas.% table is missing', table_name;
    END IF;
  END LOOP;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'atlas.comparison_runs'::regclass
      AND contype = 'u'
      AND pg_get_constraintdef(oid) LIKE '%visitor_key_hash%idempotency_key%'
  ) THEN
    RAISE EXCEPTION 'comparison run idempotency uniqueness is missing';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'atlas.comparison_runs'::regclass
      AND contype = 'f'
      AND pg_get_constraintdef(oid) LIKE '%corpus_snapshot_id%'
  ) THEN
    RAISE EXCEPTION 'comparison runs must reference an immutable corpus snapshot';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'atlas.comparison_cell_evidence'::regclass
      AND contype = 'f'
      AND pg_get_constraintdef(oid) LIKE '%chunk_id%'
  ) THEN
    RAISE EXCEPTION 'comparison evidence links must reference corpus chunks';
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'atlas'
      AND indexname = 'comparison_runs_expires_idx'
  ) THEN
    RAISE EXCEPTION 'comparison retention index is missing';
  END IF;
END
$$;

SELECT 'comparison persistence contract passed' AS result;
