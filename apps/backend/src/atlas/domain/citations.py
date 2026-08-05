"""Canonical citation assembly and human-readable claim labels."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime
from uuid import UUID

from pydantic import Field

from .base import DomainModel
from .enums import ClaimType, SourceType
from .schemas import Claim, Evidence


class CitationRecord(DomainModel):
    """Public citation metadata copied only from a captured evidence record."""

    id: UUID
    evidence_id: UUID
    source_title: str = Field(min_length=1, max_length=500)
    publisher: str = Field(min_length=1, max_length=500)
    canonical_url: str
    source_revision_url: str | None = None
    anchor: str | None = None
    excerpt: str = Field(min_length=1, max_length=8000)
    captured_at: datetime
    published_at: datetime | None = None
    version_label: str | None = None
    source_type: SourceType


def assemble_citations(
    evidence: Sequence[Evidence],
    *,
    evidence_ids: Iterable[UUID],
) -> list[CitationRecord]:
    """Build stable one-to-one citation records from verified evidence only."""

    evidence_by_id = {item.id: item for item in evidence}
    citations: list[CitationRecord] = []
    seen: set[UUID] = set()
    for evidence_id in evidence_ids:
        if evidence_id in seen:
            continue
        record = evidence_by_id.get(evidence_id)
        if record is None:
            raise ValueError("citation references evidence outside the retrieved set")
        citations.append(
            CitationRecord(
                id=evidence_id,
                evidence_id=evidence_id,
                source_title=record.source_title,
                publisher=record.publisher,
                canonical_url=str(record.canonical_url),
                source_revision_url=(
                    str(record.source_revision_url)
                    if record.source_revision_url is not None
                    else None
                ),
                anchor=record.anchor,
                excerpt=record.excerpt,
                captured_at=record.captured_at,
                published_at=record.published_at,
                version_label=record.version_label,
                source_type=record.source_type,
            )
        )
        seen.add(evidence_id)
    return citations


def claim_type_label(claim: Claim) -> str:
    """Return a visible text label; callers must not rely on color alone."""

    return "Inference" if claim.type is ClaimType.INFERENCE else "Factual claim"
