"""PII-minimized review-case queue used by feedback and evaluation workflows."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal, Protocol
from uuid import UUID, uuid4

ReviewCategory = Literal[
    "incorrect_citation", "incorrect_answer", "outdated", "incomplete", "other"
]


@dataclass(frozen=True, slots=True)
class ReviewCaseRecord:
    id: UUID
    answer_run_id: UUID
    category: ReviewCategory
    label: Literal["useful", "not_useful"]
    created_at: datetime


class ReviewCaseListing(Protocol):
    def list_cases(self) -> Sequence[ReviewCaseRecord]: ...


class InMemoryReviewCaseService:
    """Deterministic local queue; production can replace it with a durable adapter."""

    def __init__(self) -> None:
        self._cases: list[ReviewCaseRecord] = []

    async def enqueue(
        self,
        answer_run_id: UUID,
        *,
        category: ReviewCategory,
        label: Literal["useful", "not_useful"],
    ) -> ReviewCaseRecord:
        record = ReviewCaseRecord(
            id=uuid4(),
            answer_run_id=answer_run_id,
            category=category,
            label=label,
            created_at=datetime.now(UTC),
        )
        self._cases.append(record)
        return record

    def list_cases(self) -> Sequence[ReviewCaseRecord]:
        return tuple(self._cases)
