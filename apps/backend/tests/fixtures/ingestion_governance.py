from datetime import UTC, datetime, timedelta

from atlas.ingestion.catalog import build_default_catalog
from atlas.ingestion.governance import InMemoryGovernanceRepository


FIXTURE_NOW = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)


def governance_repository() -> InMemoryGovernanceRepository:
    return InMemoryGovernanceRepository(
        build_default_catalog(), now=lambda: FIXTURE_NOW
    )


def seven_days_before() -> datetime:
    return FIXTURE_NOW - timedelta(days=7)
