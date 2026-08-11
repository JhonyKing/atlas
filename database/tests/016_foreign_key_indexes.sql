-- Every foreign key reported by the Supabase performance advisor must have a covering index.
DO $$
DECLARE
  index_name text;
BEGIN
  FOREACH index_name IN ARRAY ARRAY[
    'agent_review_decisions_request_idx',
    'agent_review_decisions_reviewer_idx',
    'agent_review_requests_reviewer_idx',
    'agent_runs_plan_idx',
    'answer_citations_run_claim_idx',
    'answer_citations_run_evidence_idx',
    'answer_runs_snapshot_idx',
    'chunk_embeddings_profile_idx',
    'chunks_parent_idx',
    'comparison_cell_evidence_chunk_idx',
    'comparison_runs_snapshot_idx',
    'governance_connector_runs_collection_idx',
    'governance_policy_reviews_collection_idx',
    'governance_policy_reviews_source_idx',
    'governed_source_versions_parent_idx',
    'governed_sources_current_version_idx',
    'governed_sources_private_owner_idx',
    'ingestion_items_run_idx',
    'ingestion_items_source_version_idx',
    'news_selections_candidate_idx',
    'report_jobs_source_run_idx',
    'run_evidence_chunk_idx',
    'source_versions_ingestion_run_idx',
    'sources_current_version_idx'
  ] LOOP
    IF to_regclass('atlas.' || index_name) IS NULL THEN
      RAISE EXCEPTION 'missing foreign-key index atlas.%', index_name;
    END IF;
  END LOOP;
END $$;
