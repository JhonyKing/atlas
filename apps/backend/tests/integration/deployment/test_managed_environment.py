"""Provider-neutral managed environment smoke fixtures."""

from pathlib import Path

ROOT = Path(__file__).parents[5]


def test_managed_manifest_requires_immutable_image_and_readiness() -> None:
    manifest = (ROOT / "infra/deployment/api-worker.yaml").read_text(encoding="utf-8")
    assert "@sha256:" in manifest
    assert "readinessPath: /readyz" in manifest
    assert "livenessPath: /healthz" in manifest


def test_managed_environment_has_separate_preview_and_production_templates() -> None:
    preview = (ROOT / "infra/env/preview.example").read_text(encoding="utf-8")
    production = (ROOT / "infra/env/production.example").read_text(encoding="utf-8")
    assert "api-preview" in preview
    assert "api.example" in production
    assert preview != production


def test_private_boundaries_are_present_in_database_contract_suite() -> None:
    sql_contracts = {
        path.name
        for path in (ROOT / "database/tests").glob("*.sql")
    }
    required_contracts = {
        "009_identity_rls.sql",
        "010_private_data_rls.sql",
        "011_cross_user_resources.sql",
        "015_agent_tool_rls.sql",
    }
    assert required_contracts <= sql_contracts


def test_migration_head_is_explicit_and_no_localhost_fallback_is_allowed() -> None:
    migration = (
        ROOT / "database/migrations/versions/0028_agent_tool_orchestration.py"
    ).read_text(encoding="utf-8")
    pool = (ROOT / "apps/backend/src/atlas/persistence/supabase.py").read_text(encoding="utf-8")
    assert 'revision = "0028_agent_tool_orchestration"' in migration
    assert "localhost" in pool and "ValueError" in pool
