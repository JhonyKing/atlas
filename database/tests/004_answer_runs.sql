-- T045: answer-run persistence contract tests.
\set ON_ERROR_STOP on

DO $$
DECLARE table_name text;
BEGIN
  FOREACH table_name IN ARRAY ARRAY['answer_runs', 'run_evidence', 'answer_claims', 'answer_citations'] LOOP
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
    WHERE conrelid = 'atlas.answer_runs'::regclass
      AND contype = 'u'
      AND pg_get_constraintdef(oid) LIKE '%visitor_key_hash%idempotency_key%'
  ) THEN
    RAISE EXCEPTION 'answer run idempotency uniqueness is missing';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'atlas.usage_events'::regclass
      AND conname = 'usage_events_answer_run_fk'
  ) THEN
    RAISE EXCEPTION 'usage events must reference answer runs';
  END IF;
END
$$;

SELECT 'answer run persistence contract passed' AS result;
