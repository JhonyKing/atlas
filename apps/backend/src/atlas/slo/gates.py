"""Fail-closed SLO and launch-gate calculations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SLOMeasurement:
    availability: float | None
    uncontrolled_error_rate: float | None
    normal_p95_seconds: float | None
    ttft_p50_seconds: float | None
    report_p95_seconds: float | None
    citation_precision: float | None
    estimated_cost: float | None
    cost_budget: float | None


def evaluate_gate(measurement: SLOMeasurement) -> tuple[bool, tuple[str, ...]]:
    """Return a deterministic decision; absent metrics never pass silently."""

    failures: list[str] = []
    required = {
        "availability": measurement.availability,
        "uncontrolled_error_rate": measurement.uncontrolled_error_rate,
        "normal_p95_seconds": measurement.normal_p95_seconds,
        "citation_precision": measurement.citation_precision,
        "estimated_cost": measurement.estimated_cost,
        "cost_budget": measurement.cost_budget,
    }
    failures.extend(name + " missing" for name, value in required.items() if value is None)
    if measurement.availability is not None and measurement.availability < 0.995:
        failures.append("availability below 99.5%")
    if (
        measurement.uncontrolled_error_rate is not None
        and measurement.uncontrolled_error_rate >= 0.01
    ):
        failures.append("uncontrolled errors at or above 1%")
    if measurement.normal_p95_seconds is not None and measurement.normal_p95_seconds >= 12:
        failures.append("normal p95 at or above 12 seconds")
    if measurement.ttft_p50_seconds is not None and measurement.ttft_p50_seconds >= 1.5:
        failures.append("TTFT p50 at or above 1.5 seconds")
    if measurement.report_p95_seconds is not None and measurement.report_p95_seconds >= 180:
        failures.append("report p95 at or above 3 minutes")
    if measurement.citation_precision is not None and measurement.citation_precision < 0.95:
        failures.append("citation precision below 95%")
    if (
        measurement.estimated_cost is not None
        and measurement.cost_budget is not None
        and measurement.estimated_cost > measurement.cost_budget
    ):
        failures.append("cost budget exceeded")
    return not failures, tuple(failures)
