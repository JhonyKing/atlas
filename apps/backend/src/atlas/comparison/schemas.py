"""Provider-independent contracts for evidence-backed comparisons."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, field_validator, model_validator
from pydantic.types import StringConstraints

from atlas.domain import CollectionSlug, SourceType
from atlas.domain.base import DomainModel


class ComparisonCriterion(StrEnum):
    CAPABILITY = "capability"
    TOOL_CALLING = "tool_calling"
    CONTEXT = "context"
    LATENCY = "latency"
    PRICE = "price"
    LICENSE = "license"
    FRESHNESS = "freshness"
    OPERATIONAL_RISK = "operational_risk"


class ComparisonCellState(StrEnum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    NOT_APPLICABLE = "not_applicable"
    PARTIAL = "partial"
    CONTRADICTORY = "contradictory"


class ComparisonRunStatus(StrEnum):
    ACCEPTED = "accepted"
    RETRIEVING = "retrieving"
    NORMALIZING = "normalizing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    ABSTAINED = "abstained"
    CANCELLED = "cancelled"
    FAILED = "failed"


ComparisonText = Annotated[
    str, StringConstraints(strip_whitespace=False, min_length=1, max_length=2000)
]
ComparisonLanguage = Literal["en-US", "es-MX"]


class ComparisonEvidence(DomainModel):
    """Metadata the visitor can inspect for a cited comparison cell."""

    id: UUID
    source_title: ComparisonText
    publisher: ComparisonText
    canonical_url: Annotated[str, StringConstraints(min_length=1, max_length=2000)]
    source_type: SourceType
    excerpt: Annotated[str, StringConstraints(min_length=1, max_length=8000)]
    captured_at: datetime
    version_label: Annotated[str, StringConstraints(min_length=1, max_length=64)] | None = None


class ComparisonRequest(DomainModel):
    technologies: Annotated[list[CollectionSlug], Field(min_length=2, max_length=4)]
    criteria: Annotated[list[ComparisonCriterion], Field(min_length=1)]
    product: CollectionSlug | None = None
    version: (
        Annotated[str, StringConstraints(strip_whitespace=False, min_length=1, max_length=64)]
        | None
    ) = None
    date_from: date | None = None
    date_to: date | None = None
    source_type: SourceType | None = None
    language: Annotated[
        ComparisonLanguage, StringConstraints(pattern=r"^(?:en-US|es-MX)$")
    ] = "en-US"

    def effective_source_type(self, criterion: ComparisonCriterion) -> SourceType | None:
        """Route price questions to pricing evidence, regardless of broad source filters."""

        # Price is a separate evidence lane. A caller cannot accidentally make
        # technical documentation authoritative for a commercial price claim.
        if criterion is ComparisonCriterion.PRICE:
            return SourceType.PRICING
        return self.source_type

    @field_validator("technologies")
    @classmethod
    def technologies_must_be_unique(cls, value: list[CollectionSlug]) -> list[CollectionSlug]:
        if len(value) != len(set(value)):
            raise ValueError("technologies must be unique")
        return value

    @field_validator("criteria")
    @classmethod
    def criteria_must_be_unique(cls, value: list[ComparisonCriterion]) -> list[ComparisonCriterion]:
        if len(value) != len(set(value)):
            raise ValueError("criteria must be unique")
        return value

    @model_validator(mode="after")
    def date_range_must_be_ordered(self) -> ComparisonRequest:
        if (
            self.date_from is not None
            and self.date_to is not None
            and self.date_to < self.date_from
        ):
            raise ValueError("date_to must not be earlier than date_from")
        return self


class ComparisonCell(DomainModel):
    technology_id: CollectionSlug
    criterion_id: ComparisonCriterion
    state: ComparisonCellState
    value: ComparisonText | None = None
    unit: (
        Annotated[str, StringConstraints(strip_whitespace=False, min_length=1, max_length=64)]
        | None
    ) = None
    explanation: ComparisonText | None = None
    period: Annotated[str, StringConstraints(min_length=1, max_length=64)] | None = None
    version: Annotated[str, StringConstraints(min_length=1, max_length=64)] | None = None
    evidence_ids: list[UUID] = Field(default_factory=list)
    evidence: list[ComparisonEvidence] = Field(default_factory=list)
    observed_at: datetime | None = None

    @field_validator("evidence_ids")
    @classmethod
    def evidence_ids_must_be_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("evidence_ids must be unique")
        return value

    @model_validator(mode="after")
    def enforce_cell_evidence_shape(self) -> ComparisonCell:
        if self.state in {
            ComparisonCellState.UNSUPPORTED,
            ComparisonCellState.NOT_APPLICABLE,
        }:
            if self.evidence_ids:
                raise ValueError("unsupported and not-applicable cells cannot cite evidence")
            if self.evidence:
                raise ValueError("unsupported and not-applicable cells cannot include evidence")
            if not self.explanation or not self.explanation.strip():
                raise ValueError("unsupported and not-applicable cells require an explanation")
            return self
        if self.evidence and {item.id for item in self.evidence} != set(self.evidence_ids):
            raise ValueError("comparison evidence metadata must match evidence_ids")
        if not self.evidence_ids:
            raise ValueError("populated cells require at least one evidence ID")
        if (
            self.state in {ComparisonCellState.PARTIAL, ComparisonCellState.CONTRADICTORY}
            and not self.explanation
        ):
            raise ValueError("partial and contradictory cells require an explanation")
        if self.state is ComparisonCellState.SUPPORTED and self.value is None:
            raise ValueError("supported cells require a value")
        return self


class ComparisonMatrix(DomainModel):
    technology_ids: Annotated[list[CollectionSlug], Field(min_length=2, max_length=4)]
    criterion_ids: Annotated[list[ComparisonCriterion], Field(min_length=1)]
    cells: list[ComparisonCell]
    summary: ComparisonText | None = None

    @model_validator(mode="after")
    def cells_must_cover_unique_coordinates(self) -> ComparisonMatrix:
        expected = len(self.technology_ids) * len(self.criterion_ids)
        coordinates = [(cell.technology_id, cell.criterion_id) for cell in self.cells]
        if len(coordinates) != expected or len(set(coordinates)) != expected:
            raise ValueError("cells must contain exactly one entry per technology and criterion")
        if any(cell.technology_id not in self.technology_ids for cell in self.cells):
            raise ValueError("cell technology must be selected in the matrix")
        if any(cell.criterion_id not in self.criterion_ids for cell in self.cells):
            raise ValueError("cell criterion must be selected in the matrix")
        return self


class ComparisonRun(DomainModel):
    run_id: UUID
    request_id: UUID
    visitor_key_hash: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    snapshot_id: UUID
    status: ComparisonRunStatus
    created_at: datetime
    completed_at: datetime | None = None
    retained_until: datetime

    @model_validator(mode="after")
    def enforce_lifecycle_timestamps(self) -> ComparisonRun:
        terminal = {
            ComparisonRunStatus.COMPLETED,
            ComparisonRunStatus.ABSTAINED,
            ComparisonRunStatus.CANCELLED,
            ComparisonRunStatus.FAILED,
        }
        if self.status in terminal and self.completed_at is None:
            raise ValueError("terminal comparison runs require completed_at")
        if self.status not in terminal and self.completed_at is not None:
            raise ValueError("non-terminal comparison runs cannot have completed_at")
        timestamps = {
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "retained_until": self.retained_until,
        }
        for name, value in timestamps.items():
            if value is not None and value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware")
        return self
