"""Deterministic JSONL retrieval quality evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from atlas.retrieval.metrics import calculate_metrics


def evaluate(path: Path) -> dict[str, Any]:
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    relevant = [set(case["expected_ids"]) for case in cases]
    baseline = [case["baseline_ids"] for case in cases]
    candidate = [case["candidate_ids"] for case in cases]
    baseline_metrics = calculate_metrics(
        baseline,
        relevant,
        predicted_context=[item for row in baseline for item in row],
        relevant_context=set().union(*relevant) if relevant else set(),
        cited=[item for row in baseline for item in row],
        supported_citations=set().union(*relevant) if relevant else set(),
        fresh_flags=[bool(case.get("fresh")) for case in cases],
    )
    candidate_metrics = calculate_metrics(
        candidate,
        relevant,
        predicted_context=[item for row in candidate for item in row],
        relevant_context=set().union(*relevant) if relevant else set(),
        cited=[item for row in candidate for item in row],
        supported_citations=set().union(*relevant) if relevant else set(),
        fresh_flags=[bool(case.get("fresh")) for case in cases],
    )
    return {
        "dataset": str(path),
        "case_count": len(cases),
        "baseline": {
            "hit_at_5": baseline_metrics.hit_at_5,
            "mrr": baseline_metrics.mrr,
            "context_precision": baseline_metrics.context_precision,
            "context_recall": baseline_metrics.context_recall,
            "citation_precision": baseline_metrics.citation_precision,
            "freshness": baseline_metrics.freshness,
            "latency_ms": baseline_metrics.latency_ms,
            "estimated_cost": baseline_metrics.estimated_cost,
        },
        "candidate": {
            "hit_at_5": candidate_metrics.hit_at_5,
            "mrr": candidate_metrics.mrr,
            "context_precision": candidate_metrics.context_precision,
            "context_recall": candidate_metrics.context_recall,
            "citation_precision": candidate_metrics.citation_precision,
            "freshness": candidate_metrics.freshness,
            "latency_ms": candidate_metrics.latency_ms,
            "estimated_cost": candidate_metrics.estimated_cost,
        },
        "freshness": sum(bool(case.get("fresh")) for case in cases) / len(cases)
        if cases
        else 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(evaluate(args.dataset), indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
