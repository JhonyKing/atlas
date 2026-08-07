"""Publication boundary that delegates to existing answer/report validators."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from uuid import UUID

from atlas.agent.verification import verify_draft
from atlas.domain import AnswerDraft, Evidence, Question
from atlas.reports.schemas import ReportSpec


class PublicationValidationError(ValueError):
    """The proposed artifact did not pass the existing evidence/schema contract."""


def validate_answer_for_publication(
    draft: AnswerDraft,
    evidence: Iterable[Evidence],
    *,
    question: Question,
    request_id: UUID | None = None,
) -> AnswerDraft:
    result = verify_draft(draft, evidence, question=question, request_id=request_id)
    if result.error is not None or result.draft is None:
        raise PublicationValidationError(
            result.error.message if result.error else "answer validation failed"
        )
    return result.draft


def validate_report_spec_for_publication(payload: Mapping[str, object]) -> ReportSpec:
    try:
        return ReportSpec.model_validate(payload)
    except ValueError as exc:
        raise PublicationValidationError("report specification is invalid") from exc
