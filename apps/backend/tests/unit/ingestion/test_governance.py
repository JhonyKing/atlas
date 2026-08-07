from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from atlas.ingestion.catalog import build_default_catalog
from atlas.ingestion.governance import (
    GovernanceError,
    InMemoryGovernanceRepository,
    PolicyState,
)


def test_default_catalog_has_required_framework_and_provider_coverage() -> None:
    catalog = build_default_catalog()
    assert len(catalog) == 16
    assert sum(item.kind == "framework" for item in catalog) == 10
    assert sum(item.kind == "model_provider" for item in catalog) == 6
    assert all(item.allowed_hosts for item in catalog)


def test_unapproved_collection_cannot_capture_a_source() -> None:
    catalog = build_default_catalog()
    disabled = replace(catalog[0], policy_state=PolicyState.PENDING)
    repository = InMemoryGovernanceRepository([disabled, *catalog[1:]])
    with pytest.raises(GovernanceError, match="policy review"):
        repository.capture(
            collection=disabled.slug,
            url=f"https://{next(iter(disabled.allowed_hosts))}{disabled.allowed_paths[0]}guide.md",
            title="Guide",
            normalized_markdown="# Guide",
            content_sha256="a" * 64,
        )


def test_changed_content_creates_child_version_and_unchanged_is_explicit() -> None:
    repository = InMemoryGovernanceRepository(build_default_catalog())
    collection = build_default_catalog()[0]
    url = f"https://{next(iter(collection.allowed_hosts))}{collection.allowed_paths[0]}guide.md"
    first = repository.capture(
        collection=collection.slug,
        url=url,
        title="Guide",
        normalized_markdown="# Guide\n\nOne",
        content_sha256="a" * 64,
    )
    unchanged = repository.capture(
        collection=collection.slug,
        url=url,
        title="Guide",
        normalized_markdown="# Guide\n\nOne",
        content_sha256="a" * 64,
    )
    changed = repository.capture(
        collection=collection.slug,
        url=url,
        title="Guide",
        normalized_markdown="# Guide\n\nTwo",
        content_sha256="b" * 64,
    )
    assert first.outcome == "new"
    assert unchanged.outcome == "unchanged"
    assert changed.outcome == "changed"
    assert changed.version.parent_version_id == first.version.version_id
    assert repository.current_version(first.source.source_id).content_sha256 == "b" * 64


def test_stale_and_disable_states_are_visible_without_deleting_history() -> None:
    now = datetime(2026, 8, 6, tzinfo=UTC)
    catalog = build_default_catalog()
    repository = InMemoryGovernanceRepository(catalog, now=lambda: now)
    collection = catalog[0]
    url = f"https://{next(iter(collection.allowed_hosts))}{collection.allowed_paths[0]}old.md"
    captured = repository.capture(
        collection=collection.slug,
        url=url,
        title="Old",
        normalized_markdown="# Old",
        content_sha256="c" * 64,
        captured_at=now - timedelta(hours=collection.ttl_hours + 1),
    )
    assert repository.source(captured.source.source_id).state == "stale"
    repository.disable_collection(collection.slug, reason="policy correction")
    assert repository.source(captured.source.source_id).state == "disabled"
    assert len(repository.versions(captured.source.source_id)) == 1
