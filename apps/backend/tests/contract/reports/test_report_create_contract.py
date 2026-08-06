from fastapi.testclient import TestClient

from atlas.api.main import create_app


def test_report_openapi_contract_exposes_lifecycle_and_downloads() -> None:
    paths = TestClient(create_app()).get("/openapi.json").json()["paths"]
    assert "/v1/reports" in paths
    assert "/v1/reports/{report_id}" in paths
    assert "/v1/reports/{report_id}/events" in paths
    assert "/v1/reports/{report_id}/download" in paths
    assert "post" in paths["/v1/reports"]
    assert "delete" in paths["/v1/reports/{report_id}"]

