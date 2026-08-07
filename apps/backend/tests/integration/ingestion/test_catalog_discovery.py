from atlas.ingestion.catalog import build_default_catalog
from atlas.ingestion.governance import InMemoryGovernanceRepository


def test_catalog_discovery_covers_frameworks_and_model_providers() -> None:
    repository = InMemoryGovernanceRepository(build_default_catalog())
    rows = repository.coverage().collections
    assert {row["kind"] for row in rows} == {"framework", "model_provider"}
    assert sum(row["kind"] == "framework" for row in rows) == 10
    assert sum(row["kind"] == "model_provider" for row in rows) == 6
