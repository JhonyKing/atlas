"""Add covering indexes for every currently unindexed ATLAS foreign key."""

from alembic import op
import sqlalchemy as sa


revision = "foreign_key_indexes"
down_revision = "agent_tool_rls"
branch_labels = None
depends_on = None


_INDEXES = (
    ("agent_review_decisions_request_idx", "agent_review_decisions", "request_id"),
    ("agent_review_decisions_reviewer_idx", "agent_review_decisions", "reviewer_id"),
    ("agent_review_requests_reviewer_idx", "agent_review_requests", "reviewer_id"),
    ("agent_runs_plan_idx", "agent_runs", "plan_id"),
    ("answer_citations_run_claim_idx", "answer_citations", "answer_run_id, claim_id"),
    ("answer_citations_run_evidence_idx", "answer_citations", "answer_run_id, evidence_id"),
    ("answer_runs_snapshot_idx", "answer_runs", "corpus_snapshot_id"),
    ("chunk_embeddings_profile_idx", "chunk_embeddings", "embedding_profile_id"),
    ("chunks_parent_idx", "chunks", "parent_chunk_id"),
    ("comparison_cell_evidence_chunk_idx", "comparison_cell_evidence", "chunk_id"),
    ("comparison_runs_snapshot_idx", "comparison_runs", "corpus_snapshot_id"),
    ("governance_connector_runs_collection_idx", "governance_connector_runs", "collection_slug"),
    ("governance_policy_reviews_collection_idx", "governance_policy_reviews", "collection_slug"),
    ("governance_policy_reviews_source_idx", "governance_policy_reviews", "source_id"),
    ("governed_source_versions_parent_idx", "governed_source_versions", "parent_version_id"),
    ("governed_sources_current_version_idx", "governed_sources", "current_version_id"),
    ("governed_sources_private_owner_idx", "governed_sources", "private_owner_id"),
    ("ingestion_items_run_idx", "ingestion_items", "ingestion_run_id"),
    ("ingestion_items_source_version_idx", "ingestion_items", "source_version_id"),
    ("news_selections_candidate_idx", "news_selections", "candidate_id"),
    ("report_jobs_source_run_idx", "report_jobs", "source_run_id"),
    ("run_evidence_chunk_idx", "run_evidence", "chunk_id"),
    ("source_versions_ingestion_run_idx", "source_versions", "ingestion_run_id"),
    ("sources_current_version_idx", "sources", "current_version_id"),
)


def upgrade() -> None:
    for name, table, columns in _INDEXES:
        op.execute(sa.text(f"CREATE INDEX IF NOT EXISTS {name} ON atlas.{table} ({columns})"))


def downgrade() -> None:
    for name, _, _ in reversed(_INDEXES):
        op.execute(sa.text(f"DROP INDEX IF EXISTS atlas.{name}"))
