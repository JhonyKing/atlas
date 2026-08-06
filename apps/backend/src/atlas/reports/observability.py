"""Non-sensitive report metadata used for reproducibility and tracing."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ReportTraceMetadata:
    request_id: UUID
    report_id: UUID
    source_run_id: UUID
    model: str
    prompt_version: str
    corpus_snapshot: str | None
