"""Rollback remains non-destructive and operator-approved."""

from pathlib import Path

ROOT = Path(__file__).parents[5]


def test_rollback_script_does_not_execute_external_changes_by_default() -> None:
    source = (ROOT / "scripts/verify-rollback.ps1").read_text(encoding="utf-8")
    assert "AllowExternalExecution" in source
    assert "no external deployment was changed" in source


def test_runbook_forbids_automatic_schema_downgrade() -> None:
    runbook = (ROOT / "docs/runbooks/rollback.md").read_text(encoding="utf-8")
    assert "forward-only" in runbook
    assert "destructive downgrade" in runbook
