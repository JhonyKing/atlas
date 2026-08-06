-- Feature 004 identity and ownership schema contract.
DO $$
DECLARE table_name_value text;
BEGIN
  FOREACH table_name_value IN ARRAY ARRAY['users','sessions','ownership_grants'] LOOP
    IF to_regclass('atlas.' || table_name_value) IS NULL THEN
      RAISE EXCEPTION 'missing table atlas.%', table_name_value;
    END IF;
  END LOOP;
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'atlas' AND c.relname = 'ownership_grants' AND c.relrowsecurity
  ) THEN
    RAISE EXCEPTION 'ownership_grants must have RLS enabled';
  END IF;
END $$;

SELECT proname FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = 'atlas' AND proname = 'current_subject_id';
