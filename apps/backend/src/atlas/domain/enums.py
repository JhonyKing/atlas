"""Closed vocabularies shared by API, persistence, and provider boundaries."""

from enum import StrEnum


class _StringEnum(StrEnum):
    def __str__(self) -> str:
        return self.value


class CollectionSlug(_StringEnum):
    LANGGRAPH = "langgraph"
    LANGCHAIN = "langchain"
    OPENAI = "openai"


class SourceType(_StringEnum):
    DOCUMENTATION = "documentation"
    CHANGELOG = "changelog"
    RELEASE_NOTE = "release_note"


class CollectionState(_StringEnum):
    READY = "ready"
    STALE = "stale"
    REFRESHING = "refreshing"
    UNAVAILABLE = "unavailable"


class ClaimType(_StringEnum):
    FACTUAL = "factual"
    INFERENCE = "inference"


class AnswerStatus(_StringEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    ABSTAINED = "abstained"


class ErrorCode(_StringEnum):
    INVALID_QUESTION = "invalid_question"
    UNSUPPORTED_QUESTION = "unsupported_question"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    QUOTA_EXCEEDED = "quota_exceeded"
    CORPUS_UNAVAILABLE = "corpus_unavailable"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    CITATION_VERIFICATION_FAILED = "citation_verification_failed"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"
    CANCELLED = "cancelled"
    RETENTION_EXPIRED = "retention_expired"
    INTERNAL_ERROR = "internal_error"
