from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.api.routes.answers import AnswerRunStatus


class FakeAnswerService:
    def __init__(self) -> None:
        self.run_id = UUID("00000000-0000-0000-0000-000000000321")
        self.status = AnswerRunStatus(
            run_id=self.run_id,
            status="retrieving",
            created_at=datetime(2026, 8, 4, tzinfo=UTC),
            completed_at=datetime(2026, 8, 4, 0, 0, 1, tzinfo=UTC),
        )
        self.cancel_calls = 0

    async def start(
        self,
        *,
        question: Mapping[str, object],
        visitor_key_hash: str,
        idempotency_key: str,
        request_id: UUID,
    ) -> UUID:
        del question, visitor_key_hash, idempotency_key, request_id
        return self.run_id

    async def get_status(self, run_id: UUID, *, visitor_key_hash: str) -> AnswerRunStatus | None:
        del visitor_key_hash
        return self.status if run_id == self.run_id else None

    async def cancel(self, run_id: UUID, *, visitor_key_hash: str) -> AnswerRunStatus:
        del visitor_key_hash
        if run_id != self.run_id:
            raise KeyError(run_id)
        self.cancel_calls += 1
        self.status = self.status.model_copy(update={"status": "cancelled"})
        return self.status

    async def stream(self, run_id: UUID, *, visitor_key_hash: str) -> AsyncIterator[str]:
        del visitor_key_hash
        assert run_id == self.run_id
        yield 'id: 1\nevent: run.accepted\ndata: {"stage":"accepted"}\n\n'
        yield (
            'id: 2\nevent: answer.completed\n'
            'data: {"claims":[{"text":"secret draft"}],"citations":[]}\n\n'
        )


def app_and_service() -> tuple[TestClient, FakeAnswerService]:
    service = FakeAnswerService()

    async def database_probe() -> bool:
        return True

    application = create_app(
        database_probe=database_probe,
        answer_service=service,
        visitor_hmac_secret="test-visitor-secret",
    )
    return TestClient(application), service


def answer_headers(key: str = "answer-idempotency-001") -> dict[str, str]:
    return {"Idempotency-Key": key}


def test_valid_answer_stream_has_request_and_run_ids_and_delays_claims_until_completion() -> None:
    client, _ = app_and_service()

    response = client.post(
        "/v1/answers",
        headers=answer_headers(),
        json={"question": "How does LangGraph work?", "product": "langgraph"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    UUID(response.headers["x-atlas-run-id"])
    UUID(response.headers["x-request-id"])
    assert response.text.index("event: run.accepted") < response.text.index(
        "event: answer.completed"
    )
    progress = response.text.split("event: answer.completed", 1)[0]
    assert "claims" not in progress
    assert "secret draft" in response.text


def test_invalid_question_preserves_entered_text_and_does_not_start_work() -> None:
    client, service = app_and_service()
    entered = "???"

    response = client.post(
        "/v1/answers",
        headers=answer_headers("answer-invalid-001"),
        json={"question": entered},
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["error_code"] == "invalid_question"
    assert payload["entered_text"] == entered
    assert service.cancel_calls == 0


def test_repeated_cancellation_is_repeat_safe_and_status_lookup_is_typed() -> None:
    client, service = app_and_service()
    run_id = str(service.run_id)

    first = client.delete(f"/v1/answers/{run_id}")
    repeated = client.delete(f"/v1/answers/{run_id}")
    status = client.get(f"/v1/answers/{run_id}")

    assert first.status_code == 202
    assert repeated.status_code == 202
    assert status.status_code == 200
    assert status.json()["status"] == "cancelled"
    assert service.cancel_calls == 2


def test_unrelated_multi_question_is_rejected_before_quota_or_model() -> None:
    client, _ = app_and_service()

    response = client.post(
        "/v1/answers",
        headers=answer_headers("answer-multi-001"),
        json={"question": "What is LangGraph? What is LangChain?"},
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_question"


def test_over_limit_question_preserves_entered_text() -> None:
    client, _ = app_and_service()
    entered = "a" * 2001

    response = client.post(
        "/v1/answers",
        headers=answer_headers("answer-over-limit-001"),
        json={"question": entered},
    )

    assert response.status_code == 400
    assert response.json()["entered_text"] == entered
