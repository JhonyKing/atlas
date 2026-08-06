from datetime import UTC, datetime

import pytest

from atlas.news.feeds import parse_feed
from atlas.news.scheduler import DailyNewsRefreshService


@pytest.mark.asyncio
async def test_daily_selection_is_idempotent_for_the_same_utc_day() -> None:
    candidates = parse_feed(
            b"""<rss><channel><item><title>Internet Story</title>
        <link>https://news.example/story</link>
        <pubDate>Tue, 04 Aug 2026 12:00:00 +0000</pubDate>
        </item></channel></rss>""",
        publisher="Example",
    )
    service = DailyNewsRefreshService()
    now = datetime(2026, 8, 5, 13, tzinfo=UTC)

    first = await service.refresh(candidates, now=now)
    second = await service.refresh([], now=now)

    assert first == second
    assert second.status == "ready"


def test_daily_read_path_returns_unavailable_before_a_refresh() -> None:
    service = DailyNewsRefreshService()
    result = service.get_daily(now=datetime(2026, 8, 5, tzinfo=UTC))
    assert result.status == "unavailable"
    assert result.reason_code == "no_evidence"
