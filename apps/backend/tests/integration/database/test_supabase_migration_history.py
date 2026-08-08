"""Migration-history comparison tests using bounded MCP snapshots."""

from pathlib import Path

from atlas.database.migration_manifest import load_migration_manifest
from atlas.database.supabase_workflow import RemoteSnapshot, compare_state, plan_missing_revisions


def _revisions() -> list[str]:
    root = Path(__file__).resolve().parents[5]
    return [
        item.revision_id
        for item in load_migration_manifest(root / "database" / "migrations" / "versions")
    ]


def test_remote_history_matches_all_repository_revisions() -> None:
    revisions = _revisions()
    remote = RemoteSnapshot(
        project_ref="fcbclsaytbjpywlaplbh",
        environment="development",
        remote_revisions=tuple(revisions),
    )
    assert compare_state(revisions, remote) == []
    assert plan_missing_revisions(revisions, remote.remote_revisions) == ()


def test_history_drift_reports_first_divergence() -> None:
    revisions = _revisions()
    remote = RemoteSnapshot(
        project_ref="fcbclsaytbjpywlaplbh",
        environment="development",
        remote_revisions=tuple([*revisions[:-1], "unexpected_revision"]),
    )
    findings = compare_state(revisions, remote)
    assert findings[0].kind == "revision"
    assert findings[0].severity == "blocking"
