"""Paired benchmark gate for model promotion."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    quality: float
    latency_ms: float
    estimated_cost: float


def approve_promotion(
    baseline: BenchmarkResult,
    candidate: BenchmarkResult,
    *,
    min_quality_gain: float = 0.01,
    max_latency_regression: float = 0.20,
    max_cost_regression: float = 0.20,
) -> tuple[bool, str]:
    if candidate.quality < baseline.quality + min_quality_gain:
        return False, "quality did not improve enough"
    if candidate.latency_ms > baseline.latency_ms * (1 + max_latency_regression):
        return False, "latency regression exceeded policy"
    if candidate.estimated_cost > baseline.estimated_cost * (1 + max_cost_regression):
        return False, "cost regression exceeded policy"
    return True, "candidate passed promotion gate"
