"""Fail-closed promotion gate for versioned evaluation metrics."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class PromotionThresholds:
    citation_precision: float = 0.95
    faithfulness: float = 0.90
    abstention_safety: float = 0.95
    max_cost_usd: float = 0.05
    max_latency_p95_ms: float = 3000.0


def evaluate_promotion(metrics: dict[str, Any], thresholds: PromotionThresholds | None = None) -> tuple[bool, tuple[str, ...]]:
    limits = thresholds or PromotionThresholds()
    failures: list[str] = []
    for name in ("citation_precision", "faithfulness", "abstention_safety"):
        value = metrics.get(name)
        if not isinstance(value, (int, float)) or float(value) < getattr(limits, name):
            failures.append(f"{name} below threshold")
    cost = metrics.get("cost_usd")
    if not isinstance(cost, (int, float)) or float(cost) > limits.max_cost_usd:
        failures.append("cost_usd above threshold")
    latency = metrics.get("latency_p95_ms")
    if not isinstance(latency, (int, float)) or float(latency) > limits.max_latency_p95_ms:
        failures.append("latency_p95_ms above threshold")
    return not failures, tuple(failures)


def main() -> int:
    parser = argparse.ArgumentParser(prog="atlas-eval-gate")
    parser.add_argument("metrics", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.metrics.read_text(encoding="utf-8"))
    passed, failures = evaluate_promotion(payload.get("metrics", payload))
    result = {"passed": passed, "failures": list(failures), "thresholds": asdict(PromotionThresholds())}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
