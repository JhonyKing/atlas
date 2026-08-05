"""Content-minimized LangSmith trace tree for comparison workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from atlas.observability.langsmith import TraceHandle, TraceSink


@dataclass(slots=True)
class ComparisonTraceTree:
    sink: TraceSink
    root: TraceHandle
    request_id: UUID
    run_id: UUID

    @classmethod
    def start(
        cls,
        sink: TraceSink,
        *,
        request_id: UUID,
        run_id: UUID,
        locale: str,
        technology_count: int,
        criterion_count: int,
        snapshot_id: UUID,
        model: str,
        quota_limit: int,
    ) -> ComparisonTraceTree:
        root = sink.start(
            "atlas.comparison",
            request_id=request_id,
            run_id=run_id,
            fields={
                "locale": locale,
                "technology_count": technology_count,
                "criterion_count": criterion_count,
                "corpus_snapshot": str(snapshot_id),
                "model": model,
                "retrieval_version": "comparison-hybrid-v1",
                "quota_limit": quota_limit,
                "feature": "technology-comparator",
            },
            tags=("comparison", locale),
        )
        return cls(sink=sink, root=root, request_id=request_id, run_id=run_id)

    def start_stage(
        self, stage: str, *, technology: str | None = None, criterion: str | None = None
    ) -> TraceHandle:
        fields: dict[str, Any] = {"feature": "technology-comparator"}
        if technology is not None:
            fields["technology"] = technology
        if criterion is not None:
            fields["criterion"] = criterion
        return self.sink.start(
            f"atlas.comparison.{stage}",
            request_id=self.request_id,
            run_id=self.run_id,
            run_type="retriever" if stage == "retrieval" else "chain",
            fields=fields,
            tags=("comparison", stage),
            parent=self.root,
        )

    def end(self, *, status: str, matrix_cell_count: int | None = None) -> None:
        fields = {} if matrix_cell_count is None else {"matrix_cell_count": matrix_cell_count}
        self.sink.end(self.root, status=status, fields=fields)
