from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.domain import CollectionSlug
from atlas.ingestion.service import IdempotencyConflict


class FakeOperatorService:
    def __init__(self) -> None:
        self.runs: dict[UUID, dict[str, object]] = {}
        self.keys: dict[str, UUID] = {}

    def request_refresh(
        self,
        collection: CollectionSlug,
        trigger: str,
        idempotency_key: str,
        requested_by: str | None = None,
    ) -> UUID:
        del trigger, requested_by
        if idempotency_key in self.keys:
            run_id = self.keys[idempotency_key]
            if self.runs[run_id]["collection"] != collection.value:
                raise IdempotencyConflict("idempotency key belongs to another collection")
            return run_id
        run_id = uuid4()
        self.keys[idempotency_key] = run_id
        self.runs[run_id] = {
            "id": run_id,
            "collection": collection.value,
            "trigger": "operator",
            "status": "queued",
            "requested_at": datetime.now(UTC),
            "attempt_count": 0,
            "discovered_count": 0,
            "promoted_count": 0,
            "failed_count": 0,
            "error_code": None,
        }
        return run_id

    def get_status(self, run_id: UUID) -> dict[str, object] | None:
        return self.runs.get(run_id)


def app_and_service() -> tuple[TestClient, FakeOperatorService]:
    service = FakeOperatorService()

    async def database_probe() -> bool:
        return True

    application = create_app(
        database_probe=database_probe,
        operator_service=service,
        operator_token="operator-test-token",
    )
    return TestClient(application), service


def headers(
    *,
    token: str = "operator-test-token",
    key: str = "operator-key-123456",
) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Idempotency-Key": key}


def test_operator_ingestion_requires_bearer_authentication() -> None:
    client, _ = app_and_service()

    response = client.post(
        "/v1/operator/ingestion-runs",
        headers={"Idempotency-Key": "operator-key-123456"},
        json={"collection": "langgraph"},
    )

    assert response.status_code == 401
    assert "operator-test-token" not in response.text


def test_operator_can_enqueue_and_repeat_an_idempotent_refresh() -> None:
    client, _ = app_and_service()
    request = {"collection": "langgraph"}

    first = client.post("/v1/operator/ingestion-runs", headers=headers(), json=request)
    repeated = client.post("/v1/operator/ingestion-runs", headers=headers(), json=request)

    assert first.status_code == 202
    assert repeated.status_code == 202
    assert first.json()["id"] == repeated.json()["id"]
    assert first.json()["status"] == "queued"
    assert "operator-test-token" not in first.text


def test_operator_idempotency_conflict_and_status_lookup_are_controlled() -> None:
    client, _ = app_and_service()
    key_headers = headers(key="operator-key-conflict")
    first = client.post(
        "/v1/operator/ingestion-runs",
        headers=key_headers,
        json={"collection": "langgraph"},
    )
    conflict = client.post(
        "/v1/operator/ingestion-runs",
        headers=key_headers,
        json={"collection": "openai"},
    )
    run_id = first.json()["id"]
    status = client.get(
        f"/v1/operator/ingestion-runs/{run_id}",
        headers={"Authorization": "Bearer operator-test-token"},
    )
    missing = client.get(
        f"/v1/operator/ingestion-runs/{uuid4()}",
        headers={"Authorization": "Bearer operator-test-token"},
    )

    assert conflict.status_code == 409
    assert status.status_code == 200
    assert status.json()["collection"] == "langgraph"
    assert missing.status_code == 404
