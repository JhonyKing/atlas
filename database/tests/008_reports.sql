-- Contract checks for Feature 003 report metadata and lifecycle constraints.
DO $$
DECLARE
  table_name_value text;
BEGIN
  FOREACH table_name_value IN ARRAY ARRAY['report_jobs', 'report_documents'] LOOP
    IF to_regclass('atlas.' || table_name_value) IS NULL THEN
      RAISE EXCEPTION 'missing table atlas.%', table_name_value;
    END IF;
  END LOOP;
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'report_jobs_visitor_key_hash_check'
  ) THEN
    RAISE EXCEPTION 'missing visitor ownership constraint';
  END IF;
END $$;

SELECT status
FROM atlas.report_jobs
WHERE status IN ('accepted','planning','rendering','completed','failed','cancelled','expired','deleted');

SELECT model, prompt_version
FROM atlas.report_jobs
WHERE model = 'gpt-5.6-luna' AND prompt_version = 'report-v1';
