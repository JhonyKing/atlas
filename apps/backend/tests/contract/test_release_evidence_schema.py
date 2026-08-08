"""Minimal contract validation for release evidence without a third-party schema dependency."""

import json
from datetime import datetime
from pathlib import Path


def test_release_evidence_schema_has_required_fields_and_status_enum() -> None:
    schema = json.loads(
        (
            Path(__file__).parents[4]
            / "specs/018-production-deployment/contracts/release-evidence.schema.json"
        ).read_text(encoding="utf-8")
    )
    required = set(schema["required"])
    required_fields = {
        "release_id",
        "source_revision",
        "migration_revision",
        "checks",
        "smoke_results",
        "health",
        "created_at",
    }
    assert required_fields <= required
    statuses = set(schema["$defs"]["check"]["properties"]["status"]["enum"])
    assert statuses == {"passed", "failed", "skipped"}
    assert set(schema["properties"]["health"]["required"]) == {"environment", "status"}
    datetime.fromisoformat("2026-08-07T00:00:00+00:00")
