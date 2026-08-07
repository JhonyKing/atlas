from uuid import uuid4

import pytest

from atlas.agent.review import ReviewService, ReviewStatus


def test_review_approve_is_repeat_safe() -> None:
    service = ReviewService()
    request = service.create(
        run_id=uuid4(), evidence_ids=["ev-1"], proposed_text="Verified answer", reviewer_id="user-1"
    )
    decision = service.decide(request.id, reviewer_id="user-1", action="approve", decision_key="d1")
    repeated = service.decide(request.id, reviewer_id="user-1", action="approve", decision_key="d1")
    assert decision.status is ReviewStatus.APPROVED
    assert repeated == decision


def test_edit_cannot_remove_evidence() -> None:
    service = ReviewService()
    request = service.create(
        run_id=uuid4(), evidence_ids=["ev-1"], proposed_text="Verified answer", reviewer_id="user-1"
    )
    with pytest.raises(ValueError, match="evidence"):
        service.decide(
            request.id, reviewer_id="user-1", action="edit", decision_key="d1", edited_text=""
        )


def test_rejection_is_not_publishable_and_unauthorized_decision_fails() -> None:
    service = ReviewService()
    request = service.create(
        run_id=uuid4(), evidence_ids=["ev-1"], proposed_text="Verified answer", reviewer_id="user-1"
    )
    with pytest.raises(PermissionError):
        service.decide(request.id, reviewer_id="user-2", action="approve", decision_key="d2")
    service.decide(request.id, reviewer_id="user-1", action="reject", decision_key="d3")
    assert service.can_publish(request.id) is False
