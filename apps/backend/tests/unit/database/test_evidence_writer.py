"""Tests for migration evidence persistence."""

import json
from datetime import UTC, datetime
from pathlib import Path

from atlas.database.evidence_writer import write_evidence
from atlas.database.migration_evidence import PROJECT_REF, MigrationCheck, MigrationEvidence


def test_writer_emits_schema_compatible_non_secret_json(tmp_path: Path) -> None:
    evidence = MigrationEvidence(
        run_id="writer-test",
        project_ref=PROJECT_REF,
        environment="development",
        mode="inspect",
        started_at=datetime(2026, 8, 7, tzinfo=UTC),
        finished_at=datetime(2026, 8, 7, 0, 0, 1, tzinfo=UTC),
        checks=[MigrationCheck(name="project", status="passed")],
        status="passed",
    )

    output = write_evidence(evidence, tmp_path)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert output.name == "supabase-migration-writer-test.json"
    assert payload["project_ref"] == PROJECT_REF
    assert "api_key" not in output.read_text(encoding="utf-8").lower()
