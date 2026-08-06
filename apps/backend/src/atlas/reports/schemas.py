"""Provider-independent contracts for report generation and artifacts."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from atlas.domain.base import DomainModel


class ReportType(StrEnum):
    COMPARISON = "comparison"
    ARCHITECTURE_BRIEF = "architecture_brief"
    ADR = "adr"
    RELEASE_INTELLIGENCE = "release_intelligence"
    RESEARCH = "research"


class ReportLocale(StrEnum):
    EN_US = "en-US"
    ES_MX = "es-MX"


class ReportFormat(StrEnum):
    DOCX = "docx"
    PDF = "pdf"


class ReportStatus(StrEnum):
    ACCEPTED = "accepted"
    PLANNING = "planning"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    DELETED = "deleted"


class ReportSpec(DomainModel):
    source_run_id: UUID
    report_type: ReportType = ReportType.COMPARISON
    locale: ReportLocale = ReportLocale.EN_US
    audience: Annotated[str, Field(min_length=1, max_length=200)]
    scope: Annotated[str, Field(min_length=1, max_length=500)]
    criteria: list[Annotated[str, Field(min_length=1, max_length=100)]] = Field(
        default_factory=list
    )
    required_sections: list[Annotated[str, Field(min_length=1, max_length=120)]] = Field(
        default_factory=lambda: [
            "Executive summary",
            "Comparison matrix",
            "Limitations",
            "References",
        ]
    )
    format: ReportFormat = ReportFormat.DOCX

    @field_validator("criteria", "required_sections")
    @classmethod
    def unique_values(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("values must be unique")
        return values


class ReportCitation(DomainModel):
    citation_id: str = Field(min_length=1, max_length=120)
    source_run_id: UUID
    evidence_id: UUID
    url: str = Field(min_length=1, max_length=2000)
    excerpt: str = Field(min_length=1, max_length=2000)
    original_language: str = Field(default="en", min_length=2, max_length=16)


class ReportSection(DomainModel):
    title: str = Field(min_length=1, max_length=200)
    narrative: str = Field(min_length=1, max_length=10000)
    citation_ids: list[str] = Field(default_factory=list)
    is_factual: bool = True


class ReportRepresentation(DomainModel):
    title: str
    locale: ReportLocale
    source_run_id: UUID
    sections: list[ReportSection] = Field(min_length=1)
    citations: list[ReportCitation] = Field(min_length=1)
    generated_at: datetime

    @model_validator(mode="after")
    def citations_must_be_used(self) -> ReportRepresentation:
        available = {citation.citation_id for citation in self.citations}
        for section in self.sections:
            if section.is_factual and not set(section.citation_ids).issubset(available):
                raise ValueError("section references an unknown citation")
        return self


class ReportDocument(DomainModel):
    format: ReportFormat
    content_hash: str
    size_bytes: int = Field(gt=0)
    expires_at: datetime
    download_name: str


class ReportJob(DomainModel):
    report_id: UUID
    request_id: UUID
    owner_key_hash: str = Field(min_length=1, max_length=128)
    spec: ReportSpec
    status: ReportStatus
    created_at: datetime
    completed_at: datetime | None = None
    expires_at: datetime
    document: ReportDocument | None = None
    error_code: str | None = None
