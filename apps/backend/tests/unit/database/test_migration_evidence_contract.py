"""Contract tests for the repository's JSON evidence schema."""

import json
from datetime import UTC, datetime
from pathlib import Path

from atlas.database.migration_evidence import PROJECT_REF, MigrationEvidence


def test_evidence_model_matches_required_json_schema_fields() -> None:
    root = Path(__file__).resolve().parents[5]
    schema_path = (
        root
        / "specs"
        / "021-supabase-database-migration"
        / "contracts"
        / "migration-evidence.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    payload = {
        "run_id": "contract-test",
        "project_ref": PROJECT_REF,
        "environment": "development",
        "mode": "verify",
        "started_at": datetime(2026, 8, 7, tzinfo=UTC).isoformat(),
        "finished_at": datetime(2026, 8, 7, 0, 0, 1, tzinfo=UTC).isoformat(),
        "status": "passed",
        "checks": [{"name": "schema", "status": "passed"}],
        "drift": [],
    }
    assert set(schema["required"]).issubset(payload)
    parsed = MigrationEvidence.model_validate(payload)
    assert (
        parsed.model_dump(mode="json")["project_ref"]
        == schema["properties"]["project_ref"]["const"]
    )


def test_evidence_contract_rejects_unknown_top_level_fields() -> None:
    payload = {
        "run_id": "contract-test",
        "project_ref": PROJECT_REF,
        "environment": "development",
        "mode": "verify",
        "started_at": "2026-08-07T00:00:00Z",
        "finished_at": "2026-08-07T00:00:01Z",
        "status": "passed",
        "checks": [],
        "drift": [],
        "secret": "must-not-be-added",
    }
    try:
        MigrationEvidence.model_validate(payload)
    except Exception as exc:
        assert "extra" in str(exc)
    else:
        raise AssertionError("unknown evidence fields must be rejected")
