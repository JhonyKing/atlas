from atlas.ingestion.catalog import build_default_catalog
from atlas.ingestion.governance import InMemoryGovernanceRepository


def test_coverage_reports_every_collection_even_when_empty() -> None:
    repository = InMemoryGovernanceRepository(build_default_catalog())
    snapshot = repository.coverage()
    assert snapshot.collection_count == 16
    assert len(snapshot.collections) == 16
    assert all("stale_count" in row for row in snapshot.collections)
    assert snapshot.window_days == 7
    assert snapshot.target_met is True
