-- T002: bounded news persistence contract.
\set ON_ERROR_STOP on

DO $$
DECLARE
  table_name_value text;
BEGIN
  FOREACH table_name_value IN ARRAY ARRAY['news_candidates', 'news_selections', 'news_refresh_jobs'] LOOP
    IF to_regclass('atlas.' || table_name_value) IS NULL THEN
      RAISE EXCEPTION 'atlas.% table is missing', table_name_value;
    END IF;
  END LOOP;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'atlas.news_candidates'::regclass
      AND contype = 'u'
      AND pg_get_constraintdef(oid) LIKE '%canonical_url%content_sha256%'
  ) THEN
    RAISE EXCEPTION 'news candidate URL/hash deduplication is missing';
  END IF;
END
$$;

SELECT 'daily news contract passed' AS result;
