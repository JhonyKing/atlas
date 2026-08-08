"""Promotion must depend on explicit release gates."""

from pathlib import Path

ROOT = Path(__file__).parents[5]


def test_workflows_have_migration_and_smoke_steps() -> None:
    workflow = (ROOT / ".github/workflows/deploy-production.yml").read_text(encoding="utf-8")
    assert "release-migrate.ps1" in workflow
    assert "deployment-smoke.py" in workflow
    assert "environment:" in workflow


def test_release_evidence_generator_has_secret_refusal() -> None:
    source = (ROOT / "scripts/generate-release-evidence.py").read_text(encoding="utf-8")
    assert "refusing to write" in source
    assert "SECRET_MARKERS" in source
