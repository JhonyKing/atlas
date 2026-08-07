import pytest

from atlas.ingestion.fetcher import FetcherError, FetchPolicy, SafeFetcher


def test_fetch_policy_rejects_private_and_unapproved_destinations() -> None:
    policy = FetchPolicy(allowed_hosts=frozenset({"docs.example.test"}))
    fetcher = SafeFetcher(client=None, policy=policy, resolver=lambda host: ("127.0.0.1",))  # type: ignore[arg-type]
    with pytest.raises(FetcherError, match="private"):
        fetcher._validate_destination("https://docs.example.test/guide")
    with pytest.raises(FetcherError, match="allowlist"):
        fetcher._validate_destination("https://evil.example.test/guide")
