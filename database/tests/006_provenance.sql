-- T005/T006: provenance columns and atomic promotion remain queryable.
\set ON_ERROR_STOP on

DO $$
DECLARE
  table_name_value text;
BEGIN
  FOREACH table_name_value IN ARRAY ARRAY['source_versions', 'chunks'] LOOP
    IF to_regclass('atlas.' || table_name_value) IS NULL THEN
      RAISE EXCEPTION 'atlas.% table is missing', table_name_value;
    END IF;
  END LOOP;
  IF (
    SELECT count(*) FROM information_schema.columns
    WHERE table_schema = 'atlas' AND table_name = 'source_versions'
      AND column_name = ANY(ARRAY['page_count', 'language', 'ocr_used', 'ocr_confidence'])
  ) <> 4 THEN
    RAISE EXCEPTION 'source version provenance columns are missing';
  END IF;
  IF (
    SELECT count(*) FROM information_schema.columns
    WHERE table_schema = 'atlas' AND table_name = 'chunks'
      AND column_name = ANY(ARRAY['page_start', 'page_end', 'language', 'ocr_used', 'ocr_confidence'])
  ) <> 5 THEN
    RAISE EXCEPTION 'chunk provenance columns are missing';
  END IF;
END
$$;

SELECT 'provenance contract passed' AS result;
