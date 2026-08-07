from atlas.ingestion.connectors.github_releases import parse_github_releases


def test_github_release_adapter_keeps_tags_and_rejects_non_https() -> None:
    records = parse_github_releases(
        [
            {
                "html_url": "https://github.com/acme/sdk/releases/tag/v1.2.0",
                "name": "SDK 1.2.0",
                "tag_name": "v1.2.0",
                "published_at": "2026-08-01T00:00:00Z",
            },
            {"html_url": "http://evil.test/release", "tag_name": "bad"},
        ],
        collection="framework-sdk",
    )
    assert len(records) == 1
    assert records[0].version_label == "v1.2.0"
