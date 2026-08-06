from datetime import UTC, datetime, timedelta
from email.utils import format_datetime

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
    observed = datetime.now(UTC)
    published_at = observed.replace(hour=12, minute=0, second=0, microsecond=0)
    published_at = published_at - timedelta(days=1)
    candidates = parse_feed(
        f"""<rss><channel><item><title>Internet signal</title>
        <link>https://news.example/story</link>
        <pubDate>{format_datetime(published_at, usegmt=True)}</pubDate>
        <description>Bounded summary</description></item></channel></rss>""".encode(),
        publisher="Example News",
        captured_at=observed,
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
    assert payload["day"] == published_at.date().isoformat()
    assert payload["timezone"] == "UTC"
    assert payload["candidate"]["publisher"] == "Example News"
    assert payload["candidate"]["canonical_url"] == "https://news.example/story"
