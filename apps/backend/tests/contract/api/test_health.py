"""HTTP contract tests for the readiness endpoint."""

from uuid import UUID

from fastapi.testclient import TestClient

from atlas.api.main import create_app


async def database_ready() -> bool:
    return True


async def database_unavailable() -> bool:
    return False


async def database_probe_raises() -> bool:
    raise RuntimeError("database-test-password must never reach the response")


def assert_safe_request_id(response_headers: dict[str, str]) -> None:
    request_id = response_headers["x-request-id"]
    assert str(UUID(request_id)) == request_id


def test_health_returns_ready_when_database_probe_succeeds() -> None:
    with TestClient(create_app(database_probe=database_ready)) as client:
        response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ready"}}
    assert response.headers["cache-control"] == "no-store"
    assert_safe_request_id(dict(response.headers))


def test_health_returns_degraded_when_database_is_unavailable() -> None:
    with TestClient(create_app(database_probe=database_unavailable)) as client:
        response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ready"}}
    assert response.headers["cache-control"] == "no-store"
    assert_safe_request_id(dict(response.headers))


def test_health_converts_internal_probe_errors_to_content_free_degraded_response() -> None:
    with TestClient(create_app(database_probe=database_probe_raises)) as client:
        response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ready"}}
    assert "database-test-password" not in response.text
    assert "RuntimeError" not in response.text
    assert_safe_request_id(dict(response.headers))


def test_generated_openapi_documents_ready_and_degraded_responses() -> None:
    operation = create_app(database_probe=database_ready).openapi()["paths"]["/healthz"]["get"]

    assert {"200", "503"}.issubset(operation["responses"])


def test_readyz_reports_dependency_failure_separately_from_liveness() -> None:
    application = create_app(database_probe=database_unavailable)
    application.state.migration_status = "ready"
    with TestClient(application) as client:
        response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"
    assert response.json()["checks"]["database"] == "failed"
