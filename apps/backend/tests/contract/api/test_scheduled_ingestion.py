from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.domain import CollectionSlug
from atlas.ingestion.scheduled import build_scheduled_idempotency_key


class FakeScheduledRunner:
    def __init__(self) -> None:
        self.calls: list[tuple[CollectionSlug, datetime]] = []

    async def run_collection(
        self,
        collection: CollectionSlug,
        *,
        requested_at: datetime,
    ) -> dict[str, object]:
        self.calls.append((collection, requested_at))
        return {
            "run_id": uuid4(),
            "collection": collection,
            "manifest_version": "fixture-v1",
            "idempotency_key": f"cron:fixture:{collection.value}",
            "processed_runs": 1,
            "status": "succeeded",
            "attempt_count": 0,
            "discovered_count": 1,
            "promoted_count": 1,
        }


def test_scheduled_ingestion_requires_cron_secret() -> None:
    runner = FakeScheduledRunner()
    client = TestClient(
        create_app(
            cron_secret="cron-test-secret",
            scheduled_ingestion=runner,
        )
    )

    response = client.get("/v1/operator/ingestion-cron/langgraph")

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    assert runner.calls == []


def test_scheduled_ingestion_returns_redacted_bounded_summary() -> None:
    runner = FakeScheduledRunner()
    client = TestClient(
        create_app(
            cron_secret="cron-test-secret",
            scheduled_ingestion=runner,
        )
    )

    response = client.get(
        "/v1/operator/ingestion-cron/langgraph",
        headers={"Authorization": "Bearer cron-test-secret"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["collection"] == "langgraph"
    assert payload["status"] == "succeeded"
    assert payload["processed_runs"] == 1
    assert "cron-test-secret" not in response.text
    assert len(runner.calls) == 1
    assert runner.calls[0][1].tzinfo == UTC


def test_scheduled_idempotency_key_is_utc_date_and_collection_scoped() -> None:
    before_midnight = datetime(2026, 8, 12, 23, 59, tzinfo=UTC)
    after_midnight = datetime(2026, 8, 13, 0, 1, tzinfo=UTC)

    first = build_scheduled_idempotency_key(
        "expansion-v3",
        before_midnight,
        CollectionSlug.LANGGRAPH,
    )
    duplicate = build_scheduled_idempotency_key(
        "expansion-v3",
        before_midnight,
        CollectionSlug.LANGGRAPH,
    )
    next_day = build_scheduled_idempotency_key(
        "expansion-v3",
        after_midnight,
        CollectionSlug.LANGGRAPH,
    )
    other_collection = build_scheduled_idempotency_key(
        "expansion-v3",
        before_midnight,
        CollectionSlug.OPENAI,
    )

    assert first == duplicate == "cron:expansion-v3:2026-08-12:langgraph"
    assert next_day == "cron:expansion-v3:2026-08-13:langgraph"
    assert other_collection == "cron:expansion-v3:2026-08-12:openai"
