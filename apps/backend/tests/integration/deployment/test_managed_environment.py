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
