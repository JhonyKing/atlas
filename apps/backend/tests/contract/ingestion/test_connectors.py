from atlas.ingestion.catalog import build_default_catalog
from atlas.ingestion.governance import InMemoryGovernanceRepository


def test_catalog_allowlist_is_explicit_and_not_empty() -> None:
    catalog = build_default_catalog()
    assert all(item.allowed_hosts and item.allowed_paths for item in catalog)
    repository = InMemoryGovernanceRepository(catalog)
    assert repository.catalog() == catalog
