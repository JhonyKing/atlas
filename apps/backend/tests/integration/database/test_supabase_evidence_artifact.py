"""Evidence artifacts remain schema-compatible and provenance-complete."""

import json
from datetime import UTC, datetime
from pathlib import Path

from atlas.database.migration_evidence import PROJECT_REF, MigrationEvidence


def test_existing_verification_artifact_has_required_provenance() -> None:
    root = Path(__file__).resolve().parents[5]
    artifact = (
        root
        / "evals"
        / "results"
        / "supabase-migration-verify-20260807-fcbclsaytbjpywlaplbh.json"
    )
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    evidence = MigrationEvidence.model_validate(payload)
    assert evidence.project_ref == PROJECT_REF
    assert evidence.repository_revisions
    assert evidence.remote_revisions
    assert evidence.started_at <= evidence.finished_at


def test_new_artifact_can_be_validated_without_private_payloads() -> None:
    evidence = MigrationEvidence(
        run_id="integration-contract",
        project_ref=PROJECT_REF,
        environment="development",
        mode="verify",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        checks=[{"name": "provenance", "status": "passed"}],
        drift=[],
        status="passed",
    )
    assert "private" not in json.dumps(evidence.model_dump(mode="json"))
