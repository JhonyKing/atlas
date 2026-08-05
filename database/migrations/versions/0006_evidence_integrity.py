"""Enforce same-run claim/evidence links and expose canonical citation metadata."""

from __future__ import annotations

from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "0006_evidence_integrity"
down_revision = "0005_answer_runs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.answer_claims
              DROP CONSTRAINT IF EXISTS answer_claims_answer_run_id_id_key;
            ALTER TABLE atlas.answer_claims
              ADD CONSTRAINT answer_claims_answer_run_id_id_key
              UNIQUE (answer_run_id, id);

            ALTER TABLE atlas.answer_citations
              DROP CONSTRAINT IF EXISTS answer_citations_claim_id_fkey;
            ALTER TABLE atlas.answer_citations
              DROP CONSTRAINT IF EXISTS answer_citations_evidence_id_fkey;
            ALTER TABLE atlas.answer_citations
              ADD CONSTRAINT answer_citations_run_claim_fk
              FOREIGN KEY (answer_run_id, claim_id)
              REFERENCES atlas.answer_claims(answer_run_id, id)
              ON DELETE CASCADE;
            ALTER TABLE atlas.answer_citations
              ADD CONSTRAINT answer_citations_run_evidence_fk
              FOREIGN KEY (answer_run_id, evidence_id)
              REFERENCES atlas.run_evidence(answer_run_id, chunk_id)
              ON DELETE RESTRICT;

            CREATE OR REPLACE VIEW atlas.answer_citation_details AS
            SELECT
              citation.id,
              citation.answer_run_id,
              citation.claim_id,
              citation.evidence_id,
              source.title AS source_title,
              source.publisher,
              source.canonical_url,
              source_version.source_revision_url,
              chunk.anchor,
              chunk.text AS excerpt,
              source_version.fetched_at AS captured_at,
              source_version.published_at,
              source_version.version_label,
              source.source_type
            FROM atlas.answer_citations AS citation
            JOIN atlas.chunks AS chunk ON chunk.id = citation.evidence_id
            JOIN atlas.source_versions AS source_version
              ON source_version.id = chunk.source_version_id
            JOIN atlas.sources AS source ON source.id = source_version.source_id;
            """
        )
    )

    function_path = Path(__file__).resolve().parents[2] / "functions" / "get_answer_result.sql"
    op.execute(sa.text(function_path.read_text(encoding="utf-8")))


def downgrade() -> None:
    op.execute(sa.text("DROP FUNCTION IF EXISTS atlas.get_answer_result(uuid)"))
    op.execute(sa.text("DROP VIEW IF EXISTS atlas.answer_citation_details"))
    op.execute(sa.text("ALTER TABLE atlas.answer_citations DROP CONSTRAINT IF EXISTS answer_citations_run_evidence_fk"))
    op.execute(sa.text("ALTER TABLE atlas.answer_citations DROP CONSTRAINT IF EXISTS answer_citations_run_claim_fk"))
    op.execute(sa.text("ALTER TABLE atlas.answer_citations ADD CONSTRAINT answer_citations_claim_id_fkey FOREIGN KEY (claim_id) REFERENCES atlas.answer_claims(id) ON DELETE CASCADE"))
    op.execute(sa.text("ALTER TABLE atlas.answer_citations ADD CONSTRAINT answer_citations_evidence_id_fkey FOREIGN KEY (evidence_id) REFERENCES atlas.chunks(id) ON DELETE RESTRICT"))
    op.execute(sa.text("ALTER TABLE atlas.answer_claims DROP CONSTRAINT IF EXISTS answer_claims_answer_run_id_id_key"))
