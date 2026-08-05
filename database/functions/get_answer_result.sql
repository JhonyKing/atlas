-- Return one retained answer with claims and canonical citation metadata.
CREATE OR REPLACE FUNCTION atlas.get_answer_result(p_run_id uuid)
RETURNS jsonb
LANGUAGE sql
STABLE
AS $$
  SELECT jsonb_build_object(
    'run_id', ar.id,
    'status', ar.status,
    'created_at', ar.created_at,
    'completed_at', ar.completed_at,
    'answer_status', ar.answer_status,
    'claims', COALESCE((
      SELECT jsonb_agg(
        jsonb_build_object(
          'id', ac.id,
          'ordinal', ac.ordinal,
          'text', ac.text,
          'type', ac.claim_type,
          'citation_ids', COALESCE((
            SELECT jsonb_agg(citation.evidence_id ORDER BY citation.id)
            FROM atlas.answer_citations AS citation
            WHERE citation.answer_run_id = ar.id
              AND citation.claim_id = ac.id
          ), '[]'::jsonb)
        ) ORDER BY ac.ordinal
      )
      FROM atlas.answer_claims AS ac
      WHERE ac.answer_run_id = ar.id
    ), '[]'::jsonb),
    'citations', COALESCE((
      SELECT jsonb_agg(
        jsonb_build_object(
          'id', details.id,
          'evidence_id', details.evidence_id,
          'source_title', details.source_title,
          'publisher', details.publisher,
          'canonical_url', details.canonical_url,
          'source_revision_url', details.source_revision_url,
          'anchor', details.anchor,
          'excerpt', details.excerpt,
          'captured_at', details.captured_at,
          'published_at', details.published_at,
          'version_label', details.version_label,
          'source_type', details.source_type
        ) ORDER BY details.id
      )
      FROM atlas.answer_citation_details AS details
      WHERE details.answer_run_id = ar.id
    ), '[]'::jsonb),
    'limitations', COALESCE(ar.limitations, '[]'::jsonb),
    'retained_until', ar.expires_at
  )
  FROM atlas.answer_runs AS ar
  WHERE ar.id = p_run_id;
$$;
