"""Reruns must not plan duplicate or destructive changes."""

from atlas.database.supabase_workflow import RemoteSnapshot, apply_ordered, plan_missing_revisions


def test_second_apply_plan_is_a_noop() -> None:
    revisions = ("0001_foundation", "0002_sources")
    remote = RemoteSnapshot("fcbclsaytbjpywlaplbh", "development", revisions)
    assert plan_missing_revisions(revisions, remote.remote_revisions) == ()
    calls: list[str] = []
    result = apply_ordered((), calls.append)
    assert result.status == "passed"
    assert result.applied == ()
    assert calls == []
