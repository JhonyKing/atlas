"""Typed contracts used by router and provider adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TaskKind = Literal["answer", "comparison", "report", "ingestion", "evaluation"]
ReasoningEffort = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class TaskSignals:
    kind: TaskKind = "answer"
    complexity: Literal["low", "medium", "high"] = "medium"
    freshness_required: bool = False
    contradiction_detected: bool = False
    report_depth: Literal["short", "deep"] = "short"


@dataclass(frozen=True, slots=True)
class ModelSelection:
    provider: str
    model: str
    reasoning_effort: ReasoningEffort
    policy_version: str
    reason: str


@dataclass(frozen=True, slots=True)
class ModelRequest:
    prompt: str
    selection: ModelSelection
    request_id: str
