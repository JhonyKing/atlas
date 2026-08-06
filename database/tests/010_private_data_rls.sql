-- Feature 004 private upload and deletion schema contract.
DO $$
DECLARE table_name_value text;
BEGIN
  FOREACH table_name_value IN ARRAY ARRAY['private_uploads','deletion_jobs'] LOOP
    IF to_regclass('atlas.' || table_name_value) IS NULL THEN
      RAISE EXCEPTION 'missing table atlas.%', table_name_value;
    END IF;
  END LOOP;
END $$;

SELECT scan_status, parse_status FROM atlas.private_uploads
WHERE scan_status IN ('pending','clean','rejected','error')
  AND parse_status IN ('pending','parsed','rejected','error');
