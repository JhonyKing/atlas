-- T037: exact hybrid retrieval contract tests.
\set ON_ERROR_STOP on

DO $$
BEGIN
  IF to_regprocedure('atlas.search_evidence(text,text,extensions.vector,integer,uuid)') IS NULL THEN
    RAISE EXCEPTION 'atlas.search_evidence function is missing';
  END IF;
END
$$;

BEGIN;
DO $$
DECLARE
  langgraph_id uuid;
  openai_id uuid;
  run_id uuid;
  source_id uuid;
  version_id uuid;
  profile_id uuid;
  keyword_chunk_id uuid;
  vector_chunk_id uuid;
  snapshot_id uuid;
  result_ids uuid[];
  repeated_ids uuid[];
  query_embedding extensions.vector(1536) := array_fill(0::real, ARRAY[1536])::extensions.vector;
BEGIN
  INSERT INTO atlas.collections(slug, display_name, publisher, base_url, allowed_hosts)
  VALUES ('langgraph', 'T037 LangGraph', 'LangChain', 'https://docs.langchain.com/', ARRAY['docs.langchain.com'])
  ON CONFLICT (slug) DO UPDATE SET display_name = EXCLUDED.display_name
  RETURNING id INTO langgraph_id;
  INSERT INTO atlas.collections(slug, display_name, publisher, base_url, allowed_hosts)
  VALUES ('openai', 'T037 OpenAI', 'OpenAI', 'https://developers.openai.com/', ARRAY['developers.openai.com'])
  ON CONFLICT (slug) DO UPDATE SET display_name = EXCLUDED.display_name
  RETURNING id INTO openai_id;

  INSERT INTO atlas.ingestion_runs(collection_id, trigger, idempotency_key, status)
  VALUES (langgraph_id, 'operator', 't037-retrieval-run-001', 'succeeded')
  RETURNING id INTO run_id;
  INSERT INTO atlas.sources(
    collection_id, canonical_url, source_type, title, publisher, trust_tier
  ) VALUES (
    langgraph_id, 'https://docs.langchain.com/t037/retrieval', 'documentation',
    'T037 Retrieval', 'LangChain', 'official_docs'
  ) RETURNING id INTO source_id;
  INSERT INTO atlas.source_versions(
    source_id, ingestion_run_id, content_sha256, fetched_at, normalized_markdown, byte_size, status
  ) VALUES (
    source_id, run_id, repeat('e', 64), now(), '# Exact retrieval\nHybrid search combines keyword and vector candidates.',
    70, 'active'
  ) RETURNING id INTO version_id;
  UPDATE atlas.sources SET current_version_id = version_id WHERE id = source_id;
  INSERT INTO atlas.chunks(
    source_version_id, ordinal, heading_path, text, text_sha256, token_count, start_offset, end_offset
  ) VALUES (
    version_id, 0, ARRAY['Exact retrieval'],
    'Hybrid search combines keyword and vector candidates.', repeat('f', 64), 8, 0, 54
  ) RETURNING id INTO keyword_chunk_id;
  INSERT INTO atlas.chunks(
    source_version_id, ordinal, heading_path, text, text_sha256, token_count, start_offset, end_offset
  ) VALUES (
    version_id, 1, ARRAY['Vector'], 'Semantic nearest neighbor result.', repeat('1', 64), 5, 55, 88
  ) RETURNING id INTO vector_chunk_id;
  INSERT INTO atlas.embedding_profiles(provider, model, dimensions, distance_metric, normalization_version)
  VALUES ('test', 't037', 1536, 'cosine', 't037') RETURNING id INTO profile_id;
  INSERT INTO atlas.chunk_embeddings(chunk_id, embedding_profile_id, embedding)
  VALUES
    (keyword_chunk_id, profile_id, query_embedding),
    (vector_chunk_id, profile_id, ('[1,' || repeat('0,', 1534) || '0]')::extensions.vector);

  INSERT INTO atlas.corpus_snapshots(revision, manifest, manifest_sha256)
  VALUES (
    nextval('atlas.corpus_snapshot_revision_seq'),
    jsonb_build_object('source_version_ids', jsonb_build_array(version_id::text)),
    repeat('2', 64)
  ) RETURNING id INTO snapshot_id;

  SELECT array_agg(evidence_id ORDER BY fused_rank) INTO result_ids
  FROM atlas.search_evidence('langgraph', 'hybrid search', query_embedding, 8, snapshot_id);
  SELECT array_agg(evidence_id ORDER BY fused_rank) INTO repeated_ids
  FROM atlas.search_evidence('langgraph', 'hybrid search', query_embedding, 8, snapshot_id);
  IF result_ids IS NULL OR cardinality(result_ids) < 2 THEN
    RAISE EXCEPTION 'hybrid retrieval did not return keyword and vector candidates';
  END IF;
  IF result_ids <> repeated_ids THEN
    RAISE EXCEPTION 'retrieval ordering is not deterministic';
  END IF;
  IF NOT (keyword_chunk_id = ANY(result_ids) AND vector_chunk_id = ANY(result_ids)) THEN
    RAISE EXCEPTION 'retrieval evidence IDs are not stable chunk IDs';
  END IF;
  IF EXISTS (
    SELECT 1 FROM atlas.search_evidence('openai', 'hybrid search', query_embedding, 8, snapshot_id)
  ) THEN
    RAISE EXCEPTION 'collection filter leaked another collection';
  END IF;
END
$$;
ROLLBACK;

SELECT 'hybrid retrieval contract passed' AS result;
