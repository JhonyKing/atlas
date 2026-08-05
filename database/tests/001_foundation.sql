-- T012: foundation database contract tests.
-- Run after the versioned migration with:
--   psql "$ATLAS_DATABASE_URL" -v ON_ERROR_STOP=1 -f database/tests/001_foundation.sql

\set ON_ERROR_STOP on

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'atlas') THEN
    RAISE EXCEPTION 'atlas schema is missing';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'atlas_private') THEN
    RAISE EXCEPTION 'atlas_private schema is missing';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'atlas_audit') THEN
    RAISE EXCEPTION 'atlas_audit schema is missing';
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
    RAISE EXCEPTION 'vector extension is missing';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM atlas.extension_status
    WHERE extension_name IN ('pgmq', 'pg_cron')
  ) THEN
    RAISE EXCEPTION 'optional queue/scheduler extension status is not recorded';
  END IF;
END
$$;

DO $$
BEGIN
  IF to_regprocedure('atlas.new_uuid()') IS NULL THEN
    RAISE EXCEPTION 'atlas.new_uuid helper is missing';
  END IF;
  IF to_regprocedure('atlas.touch_updated_at()') IS NULL THEN
    RAISE EXCEPTION 'atlas.touch_updated_at helper is missing';
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'atlas_api') THEN
    RAISE EXCEPTION 'atlas_api role is missing';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'atlas_worker') THEN
    RAISE EXCEPTION 'atlas_worker role is missing';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'atlas_migrator') THEN
    RAISE EXCEPTION 'atlas_migrator role is missing';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'atlas_readonly') THEN
    RAISE EXCEPTION 'atlas_readonly role is missing';
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'atlas'
      AND c.relname = 'app_metadata'
      AND c.relrowsecurity
  ) THEN
    RAISE EXCEPTION 'atlas.app_metadata must have row-level security enabled';
  END IF;
  IF has_schema_privilege('public', 'atlas', 'USAGE') THEN
    RAISE EXCEPTION 'public must not have usage on atlas schema';
  END IF;
END
$$;

SELECT 'foundation contract passed' AS result;
