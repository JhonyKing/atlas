from datetime import UTC, datetime

import httpx
import pytest

from atlas.ingestion.fetcher import FetcherError, FetchPolicy, SafeFetcher

NOW = datetime(2026, 8, 4, 12, 0, tzinfo=UTC)


def make_fetcher(
    handler,
    *,
    hosts: frozenset[str] = frozenset({"docs.example"}),
    resolver=lambda host: ["93.184.216.34"],
    max_bytes: int = 1024,
) -> SafeFetcher:
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return SafeFetcher(
        client=client,
        policy=FetchPolicy(allowed_hosts=hosts, max_bytes=max_bytes),
        resolver=resolver,
        clock=lambda: NOW,
    )


@pytest.mark.asyncio
async def test_fetcher_accepts_allowlisted_markdown_and_returns_metadata() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/markdown", "etag": '"abc"'},
            content=b"# Official docs\n\nContent.",
        )

    fetcher = make_fetcher(handler)
    try:
        result = await fetcher.fetch("https://docs.example/guide.md")
    finally:
        await fetcher.aclose()

    assert result.final_url == "https://docs.example/guide.md"
    assert result.content_type == "text/markdown"
    assert result.content == b"# Official docs\n\nContent."
    assert result.fetched_at == NOW
    assert result.etag == '"abc"'


@pytest.mark.asyncio
async def test_fetcher_rejects_non_allowlisted_hosts_and_private_resolution() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/plain"}, content=b"data")

    not_allowed = make_fetcher(handler)
    try:
        with pytest.raises(FetcherError, match="allowlist"):
            await not_allowed.fetch("https://evil.example/guide")
    finally:
        await not_allowed.aclose()

    private = make_fetcher(handler, resolver=lambda host: ["127.0.0.1"])
    try:
        with pytest.raises(FetcherError, match="private"):
            await private.fetch("https://docs.example/guide")
    finally:
        await private.aclose()


@pytest.mark.asyncio
async def test_fetcher_validates_redirect_target_content_type_and_size() -> None:
    def redirect_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "https://evil.example/guide"})

    redirect = make_fetcher(redirect_handler)
    try:
        with pytest.raises(FetcherError, match="redirect"):
            await redirect.fetch("https://docs.example/guide")
    finally:
        await redirect.aclose()

    def html_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/octet-stream"},
            content=b"data",
        )

    wrong_type = make_fetcher(html_handler)
    try:
        with pytest.raises(FetcherError, match="content type"):
            await wrong_type.fetch("https://docs.example/file")
    finally:
        await wrong_type.aclose()

    too_large = make_fetcher(
        lambda request: httpx.Response(
            200,
            headers={"content-type": "text/plain", "content-length": "99"},
            content=b"data",
        ),
        max_bytes=10,
    )
    try:
        with pytest.raises(FetcherError, match="size"):
            await too_large.fetch("https://docs.example/large")
    finally:
        await too_large.aclose()
