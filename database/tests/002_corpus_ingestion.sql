-- T006/T027: corpus and ingestion migration contract tests.
\set ON_ERROR_STOP on

DO $$
DECLARE table_name text;
BEGIN
  FOREACH table_name IN ARRAY ARRAY[
    'collections', 'sources', 'source_versions', 'chunks', 'embedding_profiles',
    'chunk_embeddings', 'corpus_snapshots', 'ingestion_runs', 'ingestion_items',
    'ingestion_queue', 'scheduled_jobs'
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
    WHERE conrelid = 'atlas.source_versions'::regclass
      AND contype = 'u'
      AND pg_get_constraintdef(oid) LIKE '%source_id%content_sha256%'
  ) THEN
    RAISE EXCEPTION 'source version content hash uniqueness is missing';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'atlas.ingestion_runs'::regclass
      AND contype = 'u'
      AND pg_get_constraintdef(oid) LIKE '%idempotency_key%'
  ) THEN
    RAISE EXCEPTION 'ingestion idempotency constraint is missing';
  END IF;
END
$$;

BEGIN;

DO $$
DECLARE collection_id uuid;
DECLARE run_id uuid;
DECLARE source_id uuid;
DECLARE first_version uuid;
DECLARE second_version uuid;
DECLARE current_version uuid;
DECLARE run_status text;
BEGIN
  INSERT INTO atlas.collections(
    slug, display_name, publisher, base_url, allowed_hosts
  ) VALUES (
    'langgraph', 'LangGraph test', 'LangChain', 'https://docs.langchain.com/',
    ARRAY['docs.langchain.com']
  )
  ON CONFLICT (slug) DO UPDATE SET display_name = EXCLUDED.display_name
  RETURNING id INTO collection_id;

  run_id := atlas.enqueue_ingestion(collection_id, 'operator', 't027-idempotency-key');
  IF run_id <> atlas.enqueue_ingestion(collection_id, 'operator', 't027-idempotency-key') THEN
    RAISE EXCEPTION 'repeated enqueue did not return the same run';
  END IF;

  SELECT status INTO run_status FROM atlas.ingestion_runs WHERE id = run_id;
  IF run_status <> 'queued' THEN
    RAISE EXCEPTION 'new ingestion run is not queued';
  END IF;

  INSERT INTO atlas.sources(
    collection_id, canonical_url, source_type, title, publisher, trust_tier
  ) VALUES (
    collection_id, 'https://docs.langchain.com/oss/python/langgraph/t027',
    'documentation', 'T027 source', 'LangChain', 'official_docs'
  ) RETURNING id INTO source_id;

  INSERT INTO atlas.source_versions(
    source_id, ingestion_run_id, content_sha256, fetched_at,
    normalized_markdown, byte_size, status
  ) VALUES (
    source_id, run_id, repeat('a', 64), now(), '# First', 7, 'staged'
  ) RETURNING id INTO first_version;
  PERFORM atlas.promote_source_version(source_id, first_version);

  SELECT current_version_id INTO current_version
  FROM atlas.sources WHERE id = source_id;
  IF current_version <> first_version THEN
    RAISE EXCEPTION 'first staged version was not promoted';
  END IF;

  INSERT INTO atlas.source_versions(
    source_id, ingestion_run_id, content_sha256, fetched_at,
    normalized_markdown, byte_size, status
  ) VALUES (
    source_id, run_id, repeat('b', 64), now(), '# Second', 8, 'staged'
  ) RETURNING id INTO second_version;

  SELECT current_version_id INTO current_version
  FROM atlas.sources WHERE id = source_id;
  IF current_version <> first_version THEN
    RAISE EXCEPTION 'failed refresh changed active version without promotion';
  END IF;

  PERFORM atlas.promote_source_version(source_id, second_version);
  IF (SELECT current_version_id FROM atlas.sources WHERE id = source_id) <> second_version THEN
    RAISE EXCEPTION 'second staged version was not promoted';
  END IF;
  IF (SELECT status FROM atlas.source_versions WHERE id = first_version) <> 'superseded' THEN
    RAISE EXCEPTION 'previous active version was not superseded';
  END IF;

  PERFORM atlas.fail_ingestion_run(run_id, 'fixture_failure', 2);
  IF (SELECT status FROM atlas.ingestion_runs WHERE id = run_id) <> 'failed' THEN
    RAISE EXCEPTION 'first bounded failure was not failed';
  END IF;
  PERFORM atlas.fail_ingestion_run(run_id, 'fixture_failure', 2);
  IF (SELECT status FROM atlas.ingestion_runs WHERE id = run_id) <> 'dead_letter' THEN
    RAISE EXCEPTION 'retry exhaustion did not reach dead_letter';
  END IF;
END
$$;

DO $$
DECLARE snapshot_id uuid;
BEGIN
  INSERT INTO atlas.corpus_snapshots(revision, manifest, manifest_sha256)
  VALUES (nextval('atlas.corpus_snapshot_revision_seq'), '{}'::jsonb, repeat('c', 64))
  RETURNING id INTO snapshot_id;
  IF snapshot_id IS NULL THEN
    RAISE EXCEPTION 'corpus snapshot id was not generated';
  END IF;
END
$$;

ROLLBACK;

SELECT 'corpus ingestion contract passed' AS result;
