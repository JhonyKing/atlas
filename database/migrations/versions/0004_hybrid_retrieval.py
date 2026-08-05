"""Add exact hybrid retrieval with deterministic reciprocal-rank fusion."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_hybrid_retrieval"
down_revision = "0003_anonymous_quota"
branch_labels = None
depends_on = None


_SEARCH_FUNCTION = """
CREATE OR REPLACE FUNCTION atlas.search_evidence(
  p_collection_slug text,
  p_query text,
  p_embedding vector(1536),
  p_limit integer DEFAULT 8,
  p_snapshot_id uuid DEFAULT NULL
) RETURNS TABLE(
  evidence_id uuid, chunk_id uuid, source_id uuid, source_version_id uuid,
  collection_slug text, source_title text, publisher text, canonical_url text, source_type text,
  excerpt text, capture_date timestamptz, version_label text,
  keyword_rank integer, vector_rank integer, fused_rank integer
)
LANGUAGE sql STABLE
AS $$
WITH params AS (
  SELECT p_collection_slug AS collection_slug, NULLIF(trim(p_query), '') AS query_text,
         p_embedding AS query_embedding, GREATEST(1, LEAST(p_limit, 50)) AS result_limit
),
base AS (
  SELECT c.id AS chunk_id, c.source_version_id, s.id AS source_id, co.slug AS collection_slug,
         s.title AS source_title, s.publisher, s.canonical_url, s.source_type, c.text AS excerpt,
         sv.fetched_at AS capture_date, sv.version_label, c.search_vector, ce.embedding
  FROM atlas.chunks AS c
  JOIN atlas.source_versions AS sv ON sv.id = c.source_version_id
  JOIN atlas.sources AS s ON s.id = sv.source_id
  JOIN atlas.collections AS co ON co.id = s.collection_id
  LEFT JOIN atlas.chunk_embeddings AS ce ON ce.chunk_id = c.id
  CROSS JOIN params AS p
  WHERE co.slug = p.collection_slug AND sv.status = 'active'
    AND (p_snapshot_id IS NULL OR EXISTS (
      SELECT 1 FROM atlas.corpus_snapshots AS snapshot
      WHERE snapshot.id = p_snapshot_id
        AND (snapshot.manifest -> 'source_version_ids') ? c.source_version_id::text
    ))
),
keyword_candidates AS (
  SELECT b.chunk_id, row_number() OVER (
    ORDER BY ts_rank_cd(b.search_vector, websearch_to_tsquery('english', p.query_text)) DESC,
             b.chunk_id
  )::integer AS keyword_rank
  FROM base AS b CROSS JOIN params AS p
  WHERE p.query_text IS NOT NULL
    AND b.search_vector @@ websearch_to_tsquery('english', p.query_text)
  ORDER BY ts_rank_cd(b.search_vector, websearch_to_tsquery('english', p.query_text)) DESC,
           b.chunk_id LIMIT 50
),
embedded AS (
  SELECT DISTINCT ON (b.chunk_id) b.chunk_id, b.embedding, p.query_embedding
  FROM base AS b CROSS JOIN params AS p
  WHERE b.embedding IS NOT NULL
  ORDER BY b.chunk_id, b.embedding <=> p.query_embedding
),
vector_candidates AS (
  SELECT e.chunk_id, row_number() OVER (
    ORDER BY e.embedding <=> e.query_embedding, e.chunk_id
  )::integer AS vector_rank
  FROM embedded AS e
  ORDER BY e.embedding <=> e.query_embedding, e.chunk_id LIMIT 50
),
fused AS (
  SELECT candidate.chunk_id, min(candidate.keyword_rank) AS keyword_rank,
         min(candidate.vector_rank) AS vector_rank,
         sum(1.0 / (60.0 + COALESCE(candidate.keyword_rank, candidate.vector_rank))) AS fused_score
  FROM (
    SELECT chunk_id, keyword_rank, NULL::integer AS vector_rank FROM keyword_candidates
    UNION ALL
    SELECT chunk_id, NULL::integer AS keyword_rank, vector_rank FROM vector_candidates
  ) AS candidate
  GROUP BY candidate.chunk_id
),
ordered AS (
  SELECT f.chunk_id, f.keyword_rank, f.vector_rank,
         row_number() OVER (ORDER BY f.fused_score DESC, f.chunk_id)::integer AS fused_rank
  FROM fused AS f
)
SELECT o.chunk_id AS evidence_id, o.chunk_id, b.source_id, b.source_version_id,
       b.collection_slug, b.source_title, b.publisher, b.canonical_url, b.source_type, b.excerpt,
       b.capture_date, b.version_label, o.keyword_rank, o.vector_rank, o.fused_rank
FROM ordered AS o JOIN base AS b ON b.chunk_id = o.chunk_id CROSS JOIN params AS p
WHERE o.fused_rank <= p.result_limit ORDER BY o.fused_rank;
$$;
"""


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.chunks
              ADD COLUMN IF NOT EXISTS search_vector tsvector
              GENERATED ALWAYS AS (to_tsvector('english'::regconfig, text)) STORED;
            CREATE INDEX IF NOT EXISTS chunks_search_vector_gin_idx
              ON atlas.chunks USING gin(search_vector);
            """
        )
    )
    op.execute(sa.text(_SEARCH_FUNCTION))


def downgrade() -> None:
    op.execute(sa.text("DROP FUNCTION IF EXISTS atlas.search_evidence(text,text,vector,integer,uuid)"))
    op.execute(sa.text("DROP INDEX IF EXISTS atlas.chunks_search_vector_gin_idx"))
    op.execute(sa.text("ALTER TABLE atlas.chunks DROP COLUMN IF EXISTS search_vector"))
