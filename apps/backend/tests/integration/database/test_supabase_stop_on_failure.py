"""Apply stops at the first failed revision."""

from atlas.database.supabase_workflow import apply_ordered


def test_failure_stops_later_revisions() -> None:
    calls: list[str] = []

    def apply(revision: str) -> None:
        calls.append(revision)
        if revision == "0002_sources":
            raise RuntimeError("synthetic failure")

    result = apply_ordered(("0001_foundation", "0002_sources", "0003_chunks"), apply)
    assert result.applied == ("0001_foundation",)
    assert result.failed_revision == "0002_sources"
    assert calls == ["0001_foundation", "0002_sources"]
