import httpx
import pytest

from atlas.news.fetch import FeedError, FeedPolicy, NewsFeedFetcher

RSS = b"""<rss><channel><item>
<title>Internet signal</title><link>https://news.example/story</link>
<pubDate>Tue, 04 Aug 2026 12:00:00 +0000</pubDate>
<description>Bounded summary</description>
</item></channel></rss>"""


@pytest.mark.asyncio
async def test_fetch_requires_approved_review_and_enforces_allowlist() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=RSS))
    async with httpx.AsyncClient(transport=transport) as client:
        fetcher = NewsFeedFetcher(
            client,
            policy=FeedPolicy(
                allowed_hosts=frozenset({"news.example"}),
                review_status="approved",
            ),
        )
        candidates = await fetcher.fetch(
            "https://news.example/feed.xml", publisher="Example"
        )
    assert len(candidates) == 1
    assert candidates[0].publisher == "Example"

    with pytest.raises(FeedError, match="allowlist"):
        async with httpx.AsyncClient(transport=transport) as client:
            await NewsFeedFetcher(
                client,
                policy=FeedPolicy(
                    allowed_hosts=frozenset({"other.example"}), review_status="approved"
                ),
            ).fetch("https://news.example/feed.xml", publisher="Example")


@pytest.mark.asyncio
async def test_fetch_blocks_pending_review_and_oversized_feed() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=RSS))
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(FeedError, match="not approved"):
            await NewsFeedFetcher(
                client,
                policy=FeedPolicy(
                    allowed_hosts=frozenset({"news.example"}),
                    review_status="pending_operator_approval",
                ),
            ).fetch("https://news.example/feed.xml", publisher="Example")

    oversized = httpx.MockTransport(lambda request: httpx.Response(200, content=b"x" * 12))
    async with httpx.AsyncClient(transport=oversized) as client:
        with pytest.raises(FeedError, match="size limit"):
            await NewsFeedFetcher(
                client,
                policy=FeedPolicy(
                    allowed_hosts=frozenset({"news.example"}),
                    review_status="approved",
                    max_bytes=8,
                ),
            ).fetch("https://news.example/feed.xml", publisher="Example")
