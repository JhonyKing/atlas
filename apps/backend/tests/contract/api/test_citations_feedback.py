from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.api.routes.feedback import FeedbackExpired, FeedbackNotFound
from atlas.persistence.review_cases import InMemoryReviewCaseService

RUN_ID = UUID("00000000-0000-0000-0000-000000000456")
MISSING_RUN_ID = UUID("00000000-0000-0000-0000-000000000457")
EXPIRED_RUN_ID = UUID("00000000-0000-0000-0000-000000000458")


class FakeFeedbackService:
    def __init__(self) -> None:
        self.saved: dict[tuple[UUID, str], Mapping[str, object]] = {}

    async def put(
        self,
        run_id: UUID,
        *,
        visitor_key_hash: str,
        feedback: Mapping[str, object],
    ) -> None:
        if run_id == MISSING_RUN_ID:
            raise FeedbackNotFound(run_id)
        if run_id == EXPIRED_RUN_ID:
            raise FeedbackExpired(run_id)
        self.saved[(run_id, visitor_key_hash)] = dict(feedback)


def app_and_service() -> tuple[TestClient, FakeFeedbackService, InMemoryReviewCaseService]:
    service = FakeFeedbackService()
    review_service = InMemoryReviewCaseService()

    async def database_probe() -> bool:
        return True

    application = create_app(
        database_probe=database_probe,
        feedback_service=service,
        review_case_service=review_service,
        visitor_hmac_secret="test-visitor-secret",
    )
    return TestClient(application), service, review_service


def test_retained_answer_feedback_returns_no_content() -> None:
    client, service, _ = app_and_service()

    response = client.put(
        f"/v1/answers/{RUN_ID}/feedback",
        json={"label": "useful"},
    )

    assert response.status_code == 204
    UUID(response.headers["x-request-id"])
    assert len(service.saved) == 1


def test_missing_answer_feedback_is_not_found() -> None:
    client, _, _ = app_and_service()

    response = client.put(
        f"/v1/answers/{MISSING_RUN_ID}/feedback",
        json={"label": "not_useful", "category": "incorrect_citation"},
    )

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["error_code"] == "not_found"


def test_expired_answer_feedback_returns_retention_expired() -> None:
    client, _, _ = app_and_service()

    response = client.put(
        f"/v1/answers/{EXPIRED_RUN_ID}/feedback",
        json={"label": "not_useful", "category": "outdated"},
    )

    assert response.status_code == 410
    assert response.json()["error_code"] == "retention_expired"


def test_feedback_put_replaces_the_current_visitor_value_idempotently() -> None:
    client, service, review_service = app_and_service()
    visitor_cookie = {"atlas_visitor": "v" * 32}

    first = client.put(
        f"/v1/answers/{RUN_ID}/feedback",
        cookies=visitor_cookie,
        json={"label": "useful"},
    )
    replacement = client.put(
        f"/v1/answers/{RUN_ID}/feedback",
        cookies=visitor_cookie,
        json={"label": "not_useful", "category": "incorrect_citation"},
    )

    assert first.status_code == 204
    assert replacement.status_code == 204
    assert len(service.saved) == 1
    saved = next(iter(service.saved.values()))
    assert saved["label"] == "not_useful"
    assert saved["category"] == "incorrect_citation"
    cases = review_service.list_cases()
    assert len(cases) == 1
    assert cases[0].answer_run_id == RUN_ID
    assert cases[0].category == "incorrect_citation"
