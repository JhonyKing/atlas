from datetime import UTC, datetime

from atlas.news.feeds import parse_feed
from atlas.news.ranking import InMemoryDailyNewsService, select_previous_day


def test_rss_parser_and_previous_day_selection_are_attributed() -> None:
    feed = b"""
    <rss><channel><item>
      <title>Important Internet story</title>
      <link>https://example.com/story</link>
      <pubDate>Tue, 04 Aug 2026 12:00:00 +0000</pubDate>
      <description>A bounded summary.</description>
    </item></channel></rss>
    """
    candidates = parse_feed(
        feed,
        publisher="Example News",
        captured_at=datetime(2026, 8, 5, 1, tzinfo=UTC),
        authority_score=0.9,
        topic_score=0.9,
    )

    selection = select_previous_day(candidates, now=datetime(2026, 8, 5, 13, tzinfo=UTC))

    assert selection.status == "ready"
    assert selection.day.isoformat() == "2026-08-04"
    assert selection.candidate is not None
    assert selection.candidate.publisher == "Example News"
    assert len(selection.candidate.content_sha256) == 64


def test_news_returns_unavailable_for_old_or_missing_evidence() -> None:
    feed = b"""
    <rss><channel><item>
      <title>Old story</title>
      <link>https://example.com/old</link>
      <pubDate>Mon, 03 Aug 2026 12:00:00 +0000</pubDate>
    </item></channel></rss>
    """
    candidate = parse_feed(feed, publisher="Example News")[0]
    service = InMemoryDailyNewsService([candidate])

    selection = service.get_daily(now=datetime(2026, 8, 5, 13, tzinfo=UTC))

    assert selection.status == "unavailable"
    assert selection.reason_code == "no_evidence"

