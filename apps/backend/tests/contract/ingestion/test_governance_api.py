from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.ingestion.catalog import build_default_catalog
from atlas.ingestion.governance import InMemoryGovernanceRepository


def test_governance_endpoint_returns_catalog_and_disablement() -> None:
    governance = InMemoryGovernanceRepository(build_default_catalog())
    client = TestClient(create_app(governance_service=governance))
    response = client.get("/v1/corpus/governance")
    disabled = client.post("/v1/corpus/governance/framework-langgraph/disable")
    assert response.status_code == 200
    assert len(response.json()["collections"]) == 16
    assert disabled.status_code == 202
