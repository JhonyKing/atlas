"""Unified deterministic quality checks and promotion gates."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from atlas.privacy.redaction import redact_mapping


@dataclass(frozen=True, slots=True)
class QualityResult:
    case_id: str
    passed: bool
    reasons: tuple[str, ...]
    evaluator_version: str = "quality-loop-v1"


@dataclass(frozen=True, slots=True)
class QualityGate:
    citation_precision: float | None
    schema_valid: bool | None
    estimated_cost: float | None
    cost_budget: float | None
    latency_seconds: float | None
    latency_budget_seconds: float = 12.0


@dataclass(frozen=True, slots=True)
class JudgeContract:
    judge_version: str
    criteria: tuple[str, ...]
    bias_controls: tuple[str, ...]

    def validate(self) -> None:
        if not self.judge_version.strip() or not self.criteria or not self.bias_controls:
            raise ValueError("judge version, criteria and bias controls are required")


@dataclass(frozen=True, slots=True)
class OnlineSignals:
    schema_valid: bool
    security_violation: bool
    anomaly_score: float
    latency_seconds: float
    estimated_cost: float


def evaluate_online_signals(signals: OnlineSignals) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not signals.schema_valid:
        reasons.append("format/schema signal failed")
    if signals.security_violation:
        reasons.append("security signal failed")
    if signals.anomaly_score > 1.0:
        reasons.append("anomaly threshold exceeded")
    if signals.latency_seconds < 0 or signals.estimated_cost < 0:
        reasons.append("invalid negative operational metric")
    return not reasons, tuple(reasons)


def evaluate_quality_case(case_id: str, payload: Mapping[str, Any]) -> QualityResult:
    reasons: list[str] = []
    claims = payload.get("claims")
    citations = payload.get("citations")
    if not isinstance(claims, list) or not isinstance(citations, list):
        reasons.append("schema invalid")
    citation_ids = {
        str(item.get("id")) for item in citations or [] if isinstance(item, Mapping)
    }
    linked_ids = {
        str(item)
        for claim in claims or []
        if isinstance(claim, Mapping)
        for item in claim.get("citation_ids", [])
    }
    if not linked_ids.issubset(citation_ids):
        reasons.append("citation link integrity failed")
    if len(citation_ids) != len([item for item in citations or [] if isinstance(item, Mapping)]):
        reasons.append("duplicate citation IDs")
    return QualityResult(case_id, not reasons, tuple(reasons))


def evaluate_gate(gate: QualityGate) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    required = {
        "citation_precision": gate.citation_precision,
        "schema_valid": gate.schema_valid,
        "estimated_cost": gate.estimated_cost,
        "cost_budget": gate.cost_budget,
        "latency_seconds": gate.latency_seconds,
    }
    reasons.extend(f"{name} missing" for name, value in required.items() if value is None)
    if gate.citation_precision is not None and gate.citation_precision < 0.95:
        reasons.append("citation precision below 95%")
    if gate.schema_valid is False:
        reasons.append("schema regression")
    if (
        gate.estimated_cost is not None
        and gate.cost_budget is not None
        and gate.estimated_cost > gate.cost_budget
    ):
        reasons.append("cost budget exceeded")
    if gate.latency_seconds is not None and gate.latency_seconds >= gate.latency_budget_seconds:
        reasons.append("latency budget exceeded")
    return not reasons, tuple(reasons)


def safe_trace_tags(tags: Mapping[str, Any]) -> dict[str, Any]:
    """Allow version tags and IDs while redacting content-like fields."""

    return redact_mapping(tags)
