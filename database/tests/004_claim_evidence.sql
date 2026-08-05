-- T051: claim/evidence integrity and immutable citation metadata contract tests.
\set ON_ERROR_STOP on

DO $$
DECLARE
  constraint_count integer;
BEGIN
  SELECT count(*) INTO constraint_count
  FROM pg_constraint
  WHERE conrelid = 'atlas.answer_claims'::regclass
    AND contype = 'u'
    AND pg_get_constraintdef(oid) LIKE '%answer_run_id%id%';
  IF constraint_count = 0 THEN
    RAISE EXCEPTION 'answer claims need a composite key for (answer_run_id, id)';
  END IF;

  SELECT count(*) INTO constraint_count
  FROM pg_constraint
  WHERE conrelid = 'atlas.answer_citations'::regclass
    AND contype = 'f'
    AND pg_get_constraintdef(oid) LIKE '%answer_run_id%claim_id%';
  IF constraint_count = 0 THEN
    RAISE EXCEPTION 'citations need a composite FK to the claim in the same answer run';
  END IF;

  SELECT count(*) INTO constraint_count
  FROM pg_constraint
  WHERE conrelid = 'atlas.answer_citations'::regclass
    AND contype = 'f'
    AND pg_get_constraintdef(oid) LIKE '%answer_run_id%evidence_id%';
  IF constraint_count = 0 THEN
    RAISE EXCEPTION 'citations need a composite FK to retrieved evidence in the same answer run';
  END IF;
END
$$;

DO $$
DECLARE
  required_column text;
BEGIN
  IF to_regclass('atlas.answer_citation_details') IS NULL THEN
    RAISE EXCEPTION 'canonical answer citation metadata view is missing';
  END IF;

  FOREACH required_column IN ARRAY ARRAY[
    'answer_run_id', 'claim_id', 'evidence_id', 'source_title', 'publisher',
    'canonical_url', 'source_type', 'excerpt', 'captured_at', 'published_at',
    'version_label', 'source_revision_url'
  ] LOOP
    IF NOT EXISTS (
      SELECT 1
      FROM information_schema.columns
      WHERE table_schema = 'atlas'
        AND table_name = 'answer_citation_details'
        AND column_name = required_column
    ) THEN
      RAISE EXCEPTION 'citation metadata view is missing column %', required_column;
    END IF;
  END LOOP;
END
$$;

SELECT 'claim evidence contract passed' AS result;
