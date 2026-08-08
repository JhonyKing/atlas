"""No-op verification is bounded and produces no apply calls."""

from time import perf_counter

from atlas.database.supabase_workflow import RemoteSnapshot, compare_state, plan_missing_revisions


def test_noop_verify_has_no_drift_and_is_bounded() -> None:
    revisions = tuple(f"{index:04d}_revision" for index in range(27))
    remote = RemoteSnapshot("fcbclsaytbjpywlaplbh", "development", revisions)
    started = perf_counter()
    assert compare_state(revisions, remote) == []
    assert plan_missing_revisions(revisions, remote.remote_revisions) == ()
    elapsed_ms = (perf_counter() - started) * 1000
    assert elapsed_ms < 500
