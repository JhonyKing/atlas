"""Deterministic verification gates for claims, evidence, and temporal constraints."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID, uuid4

from atlas.domain import (
    AnswerDraft,
    AnswerStatus,
    Claim,
    ControlledError,
    ErrorCode,
    Evidence,
    Question,
    VerificationStatus,
)


@dataclass(frozen=True, slots=True)
class VerificationResult:
    draft: AnswerDraft | None
    error: ControlledError | None


def verify_draft(
    draft: AnswerDraft,
    evidence: Iterable[Evidence],
    *,
    question: Question,
    request_id: UUID | None = None,
) -> VerificationResult:
    """Return only claims whose evidence and temporal constraints are deterministic."""

    evidence_list = list(evidence)
    evidence_by_id = {item.id: item for item in evidence_list}
    request = request_id or uuid4()
    if not evidence_list:
        return _failure(
            ErrorCode.INSUFFICIENT_EVIDENCE,
            "No retrieved evidence supports this question.",
            request,
        )

    if not set(draft.evidence_ids).issubset(evidence_by_id):
        return _failure(
            ErrorCode.CITATION_VERIFICATION_FAILED,
            "The draft contained an invented evidence identifier.",
            request,
        )

    temporal_error = _temporal_error(question, evidence_by_id.values(), request)
    if temporal_error is not None:
        return temporal_error

    supported: list[Claim] = []
    unsupported_found = False
    for claim in draft.claims:
        if not claim.citation_ids:
            return _failure(
                ErrorCode.CITATION_VERIFICATION_FAILED,
                "Every claim must cite retrieved evidence.",
                request,
            )
        if not set(claim.citation_ids).issubset(evidence_by_id):
            return _failure(
                ErrorCode.CITATION_VERIFICATION_FAILED,
                "The draft contained an invented evidence identifier.",
                request,
            )
        verification_status = getattr(claim, "verification_status", VerificationStatus.SUPPORTED)
        if verification_status is VerificationStatus.CONTRADICTED:
            return _failure(
                ErrorCode.CITATION_VERIFICATION_FAILED,
                "Credible sources contradict this claim; ATLAS will not choose silently.",
                request,
            )
        if verification_status is VerificationStatus.UNSUPPORTED:
            unsupported_found = True
            continue
        supported.append(claim)

    if not supported:
        return _failure(
            ErrorCode.INSUFFICIENT_EVIDENCE,
            "The available evidence does not support a principal claim.",
            request,
        )

    limitations = list(draft.limitations)
    answer_status = draft.answer_status
    if unsupported_found or answer_status is AnswerStatus.PARTIAL:
        answer_status = AnswerStatus.PARTIAL
        if not any("evidence" in limitation.casefold() for limitation in limitations):
            limitations.append(
                "Some requested claims could not be verified from the available evidence."
            )

    return VerificationResult(
        draft=AnswerDraft(
            answer_status=answer_status,
            claims=supported,
            evidence_ids=list(draft.evidence_ids),
            limitations=limitations,
        ),
        error=None,
    )


def _failure(code: ErrorCode, message: str, request_id: UUID) -> VerificationResult:
    return VerificationResult(
        draft=None,
        error=ControlledError(
            code=code,
            message=message,
            retryable=False,
            request_id=request_id,
        ),
    )


def _temporal_error(
    question: Question,
    evidence: Iterable[Evidence],
    request_id: UUID,
) -> VerificationResult | None:
    for record in evidence:
        observed_date = (record.published_at or record.captured_at).date()
        if question.date_from is not None and observed_date < question.date_from:
            return _failure(
                ErrorCode.INSUFFICIENT_EVIDENCE,
                "The available evidence is older than the requested date range.",
                request_id,
            )
        if question.date_to is not None and observed_date > question.date_to:
            return _failure(
                ErrorCode.INSUFFICIENT_EVIDENCE,
                "The available evidence is newer than the requested date range.",
                request_id,
            )
    return None
