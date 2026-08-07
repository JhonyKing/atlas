from datetime import date

from atlas.news.observability import news_observation
from atlas.news.schemas import NewsSelection


def test_news_observation_is_scalar_and_content_free() -> None:
    selection = NewsSelection(
        status="ready",
        day=date(2026, 8, 5),
        candidate_count=12,
        score=0.72,
    )

    fields = news_observation(selection, latency_ms=12.345, feed_count=4, feeds_succeeded=3)

    assert fields["status"] == "ready"
    assert fields["latency_ms"] == 12.35
    assert fields["feed_count"] == 4
    assert "title" not in fields
    assert "summary" not in fields
    assert "canonical_url" not in fields
