from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.api.routes.comparisons import ComparisonRunResponse


class FakeComparisonService:
    def __init__(self) -> None:
        self.run_id = uuid4()

    async def start(self, **kwargs: Any) -> UUID:
        return self.run_id

    async def get_status(
        self, run_id: UUID, *, visitor_key_hash: str
    ) -> ComparisonRunResponse | None:
        if run_id != self.run_id:
            return None
        return ComparisonRunResponse(
            run_id=run_id,
            status="accepted",
            created_at=datetime(2026, 8, 5, tzinfo=UTC),
        )

    async def cancel(self, run_id: UUID, *, visitor_key_hash: str) -> ComparisonRunResponse:
        return ComparisonRunResponse(
            run_id=run_id,
            status="cancelled",
            created_at=datetime(2026, 8, 5, tzinfo=UTC),
            completed_at=datetime(2026, 8, 5, 0, 1, tzinfo=UTC),
        )

    async def stream(self, run_id: UUID, *, visitor_key_hash: str) -> AsyncIterator[str]:
        yield f'id: 1\nevent: comparison.accepted\ndata: {{"run_id":"{run_id}"}}\n\n'


def test_comparison_routes_validate_and_stream_with_idempotency() -> None:
    service = FakeComparisonService()
    app = create_app(comparison_service=service)
    client = TestClient(app)
    headers = {"Idempotency-Key": "comparison-contract-key-01"}
    body = {
        "technologies": ["langgraph", "openai"],
        "criteria": ["capability", "price"],
        "language": "es-MX",
    }

    response = client.post("/v1/comparisons", json=body, headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["x-atlas-run-id"] == str(service.run_id)
    assert "comparison.accepted" in response.text

    status_response = client.get(f"/v1/comparisons/{service.run_id}")
    assert status_response.status_code == 202
    assert status_response.json()["status"] == "accepted"

    cancel_response = client.delete(f"/v1/comparisons/{service.run_id}")
    assert cancel_response.status_code == 202
    assert cancel_response.json()["status"] == "cancelled"


def test_comparison_route_rejects_missing_idempotency_key_and_invalid_selection() -> None:
    app = create_app(comparison_service=FakeComparisonService())
    client = TestClient(app)
    body = {"technologies": ["openai"], "criteria": ["capability"]}

    missing_key = client.post("/v1/comparisons", json=body)
    invalid_selection = client.post(
        "/v1/comparisons",
        json=body,
        headers={"Idempotency-Key": "comparison-contract-key-02"},
    )

    assert missing_key.status_code == 422
    assert invalid_selection.status_code == 400
