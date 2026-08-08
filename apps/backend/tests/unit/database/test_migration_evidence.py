"""Tests for the secret-safe Supabase migration evidence model."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from atlas.database.migration_evidence import PROJECT_REF, MigrationEvidence


def _valid_payload() -> dict[str, object]:
    return {
        "run_id": "run-001",
        "project_ref": PROJECT_REF,
        "environment": "development",
        "mode": "inspect",
        "started_at": datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        "finished_at": datetime(2026, 8, 7, 12, 0, 1, tzinfo=UTC),
        "schema_inventory": {"tables": ["atlas.evidence"], "extensions": ["vector"]},
        "checks": [{"name": "project", "status": "passed"}],
        "drift": [],
        "status": "passed",
    }


def test_valid_evidence_is_serializable_without_secrets() -> None:
    evidence = MigrationEvidence.model_validate(_valid_payload())

    assert evidence.project_ref == PROJECT_REF
    assert evidence.model_dump(mode="json")["status"] == "passed"


def test_evidence_rejects_other_project() -> None:
    payload = _valid_payload()
    payload["project_ref"] = "aaaaaaaaaaaaaaaaaaaa"

    with pytest.raises(ValidationError, match="must target project"):
        MigrationEvidence.model_validate(payload)


def test_evidence_rejects_secret_like_inventory_values() -> None:
    payload = _valid_payload()
    payload["schema_inventory"] = {"api_key": "sk-test-secret-value"}

    with pytest.raises(ValidationError, match="must not contain credentials"):
        MigrationEvidence.model_validate(payload)


def test_evidence_rejects_finish_before_start() -> None:
    payload = _valid_payload()
    payload["finished_at"] = datetime(2026, 8, 7, 11, 59, tzinfo=UTC)

    with pytest.raises(ValidationError, match="finished_at"):
        MigrationEvidence.model_validate(payload)
