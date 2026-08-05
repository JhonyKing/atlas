from uuid import UUID

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.persistence.review_cases import InMemoryReviewCaseService

RUN_ID = UUID("00000000-0000-0000-0000-000000000456")


def test_operator_review_cases_expose_metadata_without_content() -> None:
    reviews = InMemoryReviewCaseService()

    async def database_probe() -> bool:
        return True

    import asyncio

    asyncio.run(reviews.enqueue(RUN_ID, category="incorrect_citation", label="not_useful"))
    client = TestClient(
        create_app(
            database_probe=database_probe,
            review_case_service=reviews,
            operator_token="operator-secret",
        )
    )

    response = client.get(
        "/v1/operator/review-cases",
        headers={"Authorization": "Bearer operator-secret"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["answer_run_id"] == str(RUN_ID)
    assert set(payload[0]) == {"id", "answer_run_id", "category", "label", "created_at"}


def test_operator_review_cases_require_operator_token() -> None:
    async def database_probe() -> bool:
        return True

    client = TestClient(create_app(database_probe=database_probe))
    response = client.get("/v1/operator/review-cases")
    assert response.status_code == 401
