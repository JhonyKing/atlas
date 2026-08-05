from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import HttpUrl

from atlas.domain import (
    Claim,
    ClaimType,
    Evidence,
    SourceType,
    assemble_citations,
    claim_type_label,
)

EVIDENCE_ID = UUID("00000000-0000-0000-0000-000000000601")
NOW = datetime(2026, 8, 4, tzinfo=UTC)


def evidence() -> Evidence:
    return Evidence(
        id=EVIDENCE_ID,
        source_title="Official docs",
        publisher="Publisher",
        canonical_url=HttpUrl("https://docs.example.test/page"),
        source_revision_url=HttpUrl("https://github.com/example/docs/commit/abc123"),
        anchor="#state",
        excerpt="The captured supporting excerpt.",
        captured_at=NOW,
        published_at=NOW,
        version_label="v1.0",
        source_type=SourceType.DOCUMENTATION,
    )


def test_assemble_citations_uses_stable_evidence_ids_and_canonical_metadata() -> None:
    citations = assemble_citations([evidence()], evidence_ids=[EVIDENCE_ID, EVIDENCE_ID])

    assert len(citations) == 1
    assert citations[0].id == EVIDENCE_ID
    assert citations[0].evidence_id == EVIDENCE_ID
    assert citations[0].source_title == "Official docs"
    assert citations[0].canonical_url == "https://docs.example.test/page"


def test_assemble_citations_rejects_unretrieved_evidence() -> None:
    with pytest.raises(ValueError, match="outside the retrieved set"):
        assemble_citations([], evidence_ids=[EVIDENCE_ID])


def test_claim_type_label_is_explicit_text() -> None:
    claim = Claim(
        id=UUID("00000000-0000-0000-0000-000000000602"),
        ordinal=0,
        text="This is an inference.",
        type=ClaimType.INFERENCE,
        citation_ids=[EVIDENCE_ID],
    )

    assert claim_type_label(claim) == "Inference"
