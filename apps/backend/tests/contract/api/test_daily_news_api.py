from datetime import UTC, datetime

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.news.feeds import parse_feed
from atlas.news.ranking import InMemoryDailyNewsService


def test_daily_news_is_explicitly_unavailable_until_feed_job_is_configured() -> None:
    response = TestClient(create_app()).get("/v1/news/daily")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "unavailable"
    assert payload["reason_code"] == "not_configured"
    assert payload["timezone"] == "UTC"


def test_daily_news_ready_payload_preserves_attribution_and_previous_day() -> None:
    candidates = parse_feed(
        b"""<rss><channel><item><title>Internet signal</title>
        <link>https://news.example/story</link>
        <pubDate>Tue, 04 Aug 2026 12:00:00 +0000</pubDate>
        <description>Bounded summary</description></item></channel></rss>""",
        publisher="Example News",
        captured_at=datetime(2026, 8, 5, 1, tzinfo=UTC),
        authority_score=0.9,
        topic_score=0.9,
    )
    client = TestClient(
        create_app(
            news_service=InMemoryDailyNewsService(candidates),
        )
    )

    response = client.get("/v1/news/daily")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["day"] == "2026-08-04"
    assert payload["timezone"] == "UTC"
    assert payload["candidate"]["publisher"] == "Example News"
    assert payload["candidate"]["canonical_url"] == "https://news.example/story"
