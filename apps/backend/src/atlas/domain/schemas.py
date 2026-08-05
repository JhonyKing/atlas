"""Immutable-ish domain contracts independent of any provider SDK."""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field, HttpUrl, field_validator, model_validator
from pydantic.types import StringConstraints

from .base import DomainModel
from .enums import (
    AnswerStatus,
    ClaimType,
    CollectionSlug,
    CollectionState,
    ErrorCode,
    SourceType,
    VerificationStatus,
)

ShortText = Annotated[str, StringConstraints(strip_whitespace=False, min_length=1, max_length=500)]


class Question(DomainModel):
    """Original visitor text plus explicit constraints used for retrieval."""

    text: Annotated[str, StringConstraints(strip_whitespace=False, min_length=3, max_length=2000)]
    product: CollectionSlug | None = None
    version: Annotated[
        str, StringConstraints(strip_whitespace=False, min_length=1, max_length=64)
    ] | None = None
    date_from: date | None = None
    date_to: date | None = None
    language: Annotated[str, StringConstraints(pattern=r"^[a-z]{2}(?:-[A-Z]{2})?$")] = "en"

    @field_validator("text")
    @classmethod
    def text_must_contain_alphanumeric_content(cls, value: str) -> str:
        if not value.strip() or not any(character.isalnum() for character in value):
            raise ValueError("question must contain words or numbers")
        return value

    @model_validator(mode="after")
    def date_range_must_be_ordered(self) -> Question:
        if (
            self.date_from is not None
            and self.date_to is not None
            and self.date_to < self.date_from
        ):
            raise ValueError("date_to must not be earlier than date_from")
        return self

    @property
    def normalized_text(self) -> str:
        return " ".join(self.text.split()).casefold()


class Evidence(DomainModel):
    """Canonical evidence metadata assembled from the immutable corpus."""

    id: UUID
    source_title: ShortText
    publisher: ShortText
    canonical_url: HttpUrl
    source_revision_url: HttpUrl | None = None
    anchor: Annotated[str, StringConstraints(strip_whitespace=False, max_length=300)] | None = None
    excerpt: Annotated[
        str, StringConstraints(strip_whitespace=False, min_length=1, max_length=8000)
    ]
    captured_at: datetime
    published_at: datetime | None = None
    version_label: Annotated[
        str, StringConstraints(strip_whitespace=False, max_length=64)
    ] | None = None
    source_type: SourceType

    @field_validator("canonical_url", "source_revision_url")
    @classmethod
    def urls_must_use_https(cls, value: HttpUrl | None) -> HttpUrl | None:
        if value is not None and value.scheme != "https":
            raise ValueError("canonical evidence URLs must use HTTPS")
        return value


class Citation(DomainModel):
    """Navigable claim-to-evidence relationship; metadata is never model-authored."""

    id: UUID
    evidence_id: UUID


class Claim(DomainModel):
    """A single answer statement and the citations that support it."""

    id: UUID
    ordinal: Annotated[int, Field(ge=0)]
    text: Annotated[str, StringConstraints(strip_whitespace=False, min_length=1, max_length=2000)]
    type: ClaimType
    citation_ids: Annotated[list[UUID], Field(min_length=1)]
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.SUPPORTED,
        exclude=True,
    )

    @field_validator("text")
    @classmethod
    def claim_text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("claim text must not be blank")
        return value

    @field_validator("citation_ids")
    @classmethod
    def citation_ids_must_be_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("citation_ids must be unique")
        return value


class AnswerDraft(DomainModel):
    """Structured provider output before persistence and citation verification."""

    answer_status: AnswerStatus
    claims: list[Claim] = Field(default_factory=list)
    evidence_ids: list[UUID] = Field(default_factory=list)
    limitations: list[ShortText] = Field(default_factory=list)

    @field_validator("evidence_ids")
    @classmethod
    def evidence_ids_must_be_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("evidence_ids must be unique")
        return value

    @model_validator(mode="after")
    def enforce_abstention_shape(self) -> AnswerDraft:
        if self.answer_status is AnswerStatus.ABSTAINED and self.claims:
            raise ValueError("an abstained answer cannot contain claims")
        if self.answer_status is not AnswerStatus.ABSTAINED and not self.claims:
            raise ValueError("a non-abstained answer must contain at least one claim")
        return self


class CollectionStatus(DomainModel):
    slug: CollectionSlug
    name: ShortText
    publisher: ShortText
    source_types: Annotated[list[SourceType], Field(min_length=1)]
    status: CollectionState
    last_success_at: datetime | None = None
    last_attempt_at: datetime | None = None
    canonical_root: HttpUrl

    @field_validator("source_types")
    @classmethod
    def source_types_must_be_unique(cls, value: list[SourceType]) -> list[SourceType]:
        if len(value) != len(set(value)):
            raise ValueError("source_types must be unique")
        return value

    @field_validator("canonical_root")
    @classmethod
    def canonical_root_must_use_https(cls, value: HttpUrl) -> HttpUrl:
        if value.scheme != "https":
            raise ValueError("canonical roots must use HTTPS")
        return value


class CorpusStatus(DomainModel):
    snapshot_id: UUID
    generated_at: datetime
    collections: Annotated[list[CollectionStatus], Field(min_length=3, max_length=3)]

    @model_validator(mode="after")
    def collection_slugs_must_be_unique(self) -> CorpusStatus:
        slugs = [collection.slug for collection in self.collections]
        if len(slugs) != len(set(slugs)):
            raise ValueError("corpus collections must have unique slugs")
        return self


class ControlledError(DomainModel):
    """Safe public error payload with a closed error vocabulary."""

    code: ErrorCode
    message: Annotated[str, StringConstraints(strip_whitespace=False, min_length=1, max_length=500)]
    retryable: bool = False
    request_id: UUID
