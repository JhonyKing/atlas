from __future__ import annotations

from uuid import uuid4

from atlas.comparison.observability import ComparisonTraceTree
from atlas.observability.langsmith import TraceHandle


class RecordingTraceSink:
    def __init__(self) -> None:
        self.started: list[dict[str, object]] = []
        self.ended: list[dict[str, object]] = []

    def start(
        self, name, *, request_id, run_id, run_type="chain", fields=None, tags=(), parent=None
    ):
        self.started.append(
            {"name": name, "fields": dict(fields or {}), "tags": tuple(tags), "parent": parent}
        )
        return TraceHandle(run_id=uuid4(), active=True)

    def end(self, handle, *, status, fields=None):
        self.ended.append({"handle": handle, "status": status, "fields": dict(fields or {})})


def test_comparison_trace_tree_records_safe_metadata_and_stage_hierarchy() -> None:
    sink = RecordingTraceSink()
    tree = ComparisonTraceTree.start(
        sink,
        request_id=uuid4(),
        run_id=uuid4(),
        locale="es-MX",
        technology_count=3,
        criterion_count=2,
        snapshot_id=uuid4(),
        model="gpt-5.6-luna",
        quota_limit=5,
    )
    tree.start_stage("retrieval", technology="langgraph", criterion="capability")
    tree.end(status="completed", matrix_cell_count=6)

    assert sink.started[0]["name"] == "atlas.comparison"
    fields = sink.started[0]["fields"]
    assert fields["locale"] == "es-MX"
    assert fields["technology_count"] == 3
    assert fields["criterion_count"] == 2
    assert fields["quota_limit"] == 5
    assert "question" not in fields
    assert sink.started[1]["parent"] == tree.root
    assert sink.ended[-1]["status"] == "completed"
