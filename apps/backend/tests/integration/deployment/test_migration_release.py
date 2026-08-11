"""Forward-only migration release guard tests."""

from pathlib import Path

ROOT = Path(__file__).parents[5]


def test_release_script_defaults_to_current_migration_head() -> None:
    script = (ROOT / "scripts/release-migrate.ps1").read_text(encoding="utf-8")
    assert 'foreign_key_indexes' in script
    assert "$DryRun" in script
    assert "alembic" in script


def test_release_manifest_command_does_not_contain_downgrade() -> None:
    script = (ROOT / "scripts/release-migrate.ps1").read_text(encoding="utf-8")
    assert " downgrade " not in script.lower()
