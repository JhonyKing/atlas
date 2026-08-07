-- Feature 005 governance schema contract.
DO $$
DECLARE table_name_value text;
BEGIN
  FOREACH table_name_value IN ARRAY ARRAY[
    'governed_collections','governed_sources','governed_source_versions',
    'governance_policy_reviews','governance_connector_runs','governance_coverage_snapshots'
  ] LOOP
    IF to_regclass('atlas.' || table_name_value) IS NULL THEN
      RAISE EXCEPTION 'missing governance table atlas.%', table_name_value;
    END IF;
  END LOOP;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'atlas' AND table_name = 'governed_collections'
      AND column_name = 'robots_status'
  ) THEN
    RAISE EXCEPTION 'policy review status columns are missing';
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'governed_sources_current_version_fk'
  ) THEN
    RAISE EXCEPTION 'source current-version relation is missing';
  END IF;
END $$;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'atlas' AND table_name LIKE 'governance_%'
ORDER BY table_name;
