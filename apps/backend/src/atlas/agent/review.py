"""Authorized, idempotent human review boundary for publication."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    EDITED = "edited"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class ReviewRequest:
    id: UUID
    run_id: UUID
    evidence_ids: tuple[str, ...]
    proposed_text: str
    reviewer_id: str
    status: ReviewStatus
    expires_at: datetime
    decision_key: str | None = None


class ReviewService:
    def __init__(self, *, ttl_hours: int = 24, now: Callable[[], datetime] | None = None) -> None:
        self._ttl = timedelta(hours=ttl_hours)
        self._now = now or (lambda: datetime.now(UTC))
        self._requests: dict[UUID, ReviewRequest] = {}
        self._decisions: dict[str, ReviewRequest] = {}

    def create(
        self, *, run_id: UUID, evidence_ids: list[str], proposed_text: str, reviewer_id: str
    ) -> ReviewRequest:
        if not evidence_ids or not proposed_text.strip() or not reviewer_id.strip():
            raise ValueError("review requires evidence, proposal, and reviewer")
        now = self._now()
        request = ReviewRequest(
            uuid4(),
            run_id,
            tuple(evidence_ids),
            proposed_text,
            reviewer_id,
            ReviewStatus.PENDING,
            now + self._ttl,
        )
        self._requests[request.id] = request
        return request

    def decide(
        self,
        request_id: UUID,
        *,
        reviewer_id: str,
        action: str,
        decision_key: str,
        edited_text: str | None = None,
    ) -> ReviewRequest:
        existing_decision = self._decisions.get(decision_key)
        if existing_decision is not None:
            return existing_decision
        request = self._requests[request_id]
        if reviewer_id != request.reviewer_id:
            raise PermissionError("reviewer is not authorized")
        if request.expires_at <= self._now():
            raise ValueError("review request expired")
        if action not in {"approve", "edit", "reject"}:
            raise ValueError("unsupported review action")
        if action == "edit" and (edited_text is None or not edited_text.strip()):
            raise ValueError("edit must preserve evidence and contain text")
        status = (
            ReviewStatus.APPROVED
            if action == "approve"
            else ReviewStatus.EDITED
            if action == "edit"
            else ReviewStatus.REJECTED
        )
        updated = replace(
            request,
            status=status,
            proposed_text=edited_text or request.proposed_text,
            decision_key=hashlib.sha256(decision_key.encode()).hexdigest(),
        )
        self._requests[request_id] = updated
        self._decisions[decision_key] = updated
        return updated
