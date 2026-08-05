from fastapi.testclient import TestClient

from atlas.api.main import create_app


def test_daily_news_is_explicitly_unavailable_until_feed_job_is_configured() -> None:
    response = TestClient(create_app()).get("/v1/news/daily")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "unavailable"
    assert payload["reason_code"] == "not_configured"
    assert payload["timezone"] == "UTC"

