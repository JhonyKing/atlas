import pytest

from atlas.ingestion.catalog import build_default_catalog
from atlas.ingestion.governance import GovernanceError, InMemoryGovernanceRepository, PolicyState


def test_policy_gate_blocks_enablement_and_takedown_disables_source() -> None:
    catalog = build_default_catalog()
    repository = InMemoryGovernanceRepository(catalog)
    collection = catalog[0]
    repository.set_policy(collection.slug, PolicyState.PENDING, reason="license review")
    with pytest.raises(GovernanceError, match="approved"):
        repository.enable_collection(collection.slug)
    repository.set_policy(collection.slug, PolicyState.APPROVED, reason="approved")
    url = f"https://{next(iter(collection.allowed_hosts))}{collection.allowed_paths[0]}guide.md"
    source = repository.capture(
        collection=collection.slug,
        url=url,
        title="Guide",
        normalized_markdown="# Guide",
        content_sha256="d" * 64,
    ).source
    repository.takedown(source.source_id, reason="correction")
    assert repository.source(source.source_id).state == "disabled"


def test_enablement_requires_robots_terms_and_license_review() -> None:
    catalog = build_default_catalog()
    repository = InMemoryGovernanceRepository(catalog)
    collection = catalog[0]
    repository.review_collection(
        collection.slug,
        robots_status="pending",
        terms_status="approved",
        license_status="approved",
        reviewer="reviewer@example.test",
    )
    with pytest.raises(GovernanceError, match="review must be approved"):
        repository.enable_collection(collection.slug)
