"""Deterministic workload runner over supplied measurements."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from atlas.slo.gates import SLOMeasurement, evaluate_gate


@dataclass(frozen=True, slots=True)
class WorkloadResult:
    name: str
    requests: int
    passed: bool
    failures: tuple[str, ...]


def run_workload(
    workloads: Sequence[tuple[str, int]], measurement: SLOMeasurement
) -> list[WorkloadResult]:
    passed, failures = evaluate_gate(measurement)
    return [WorkloadResult(name, requests, passed, failures) for name, requests in workloads]
