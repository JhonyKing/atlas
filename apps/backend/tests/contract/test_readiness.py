"""Readiness response contract tests."""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from atlas.api.main import create_app


async def ready_probe() -> bool:
    return True


def test_readyz_requires_migration_head() -> None:
    app = create_app(database_probe=ready_probe)
    app.state.migration_status = "unknown"
    with TestClient(app) as client:
        response = client.get("/readyz")
    assert response.status_code == 503
    payload = response.json()
    assert payload["checks"]["database"] == "ready"
    assert payload["checks"]["migrations"] == "unknown"
    assert "password" not in response.text.lower()


def test_readyz_is_ready_when_database_and_migrations_are_ready() -> None:
    app = create_app(database_probe=ready_probe)
    app.state.migration_status = "ready"
    app.state.migration_revision = "agent_tool_rls"
    with TestClient(app) as client:
        response = client.get("/readyz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["migration_revision"] == "agent_tool_rls"


def test_production_readyz_requires_the_model_provider() -> None:
    app = create_app(database_probe=ready_probe)
    app.state.settings = SimpleNamespace(atlas_env="production")
    app.state.migration_status = "ready"
    app.state.model_provider_status = "disabled"

    with TestClient(app) as client:
        response = client.get("/readyz")

    assert response.status_code == 503
    assert response.json()["checks"]["model_provider"] == "disabled"
