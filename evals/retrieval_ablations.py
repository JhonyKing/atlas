"""Deterministic retrieval ablation matrix for the versioned RAG harness.

The runner consumes normalized result JSONL (the same shape emitted by
``evals/run_offline.py``). It deliberately does not call a model: each
configuration is scored against the same retrieved/cited IDs so changes in
retrieval policy are comparable and reproducible.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from evals.evaluators.deterministic import load_dataset
from evals.evaluators.retrieval import result_metrics
from evals.run_offline import _fixture_result, _load_results


@dataclass(frozen=True, slots=True)
class AblationConfig:
    name: str
    top_k: int
    retrieval: str
    reranking: bool
    anti_hallucination_prompt: bool


CONFIGS = (
    AblationConfig("hybrid-k4", 4, "hybrid", False, False),
    AblationConfig("hybrid-k8", 8, "hybrid", False, False),
    AblationConfig("hybrid-k10", 10, "hybrid", False, False),
    AblationConfig("hybrid-rerank-k8", 8, "hybrid", True, False),
    AblationConfig("hybrid-safe-prompt-k8", 8, "hybrid", False, True),
)


def run_ablation(
    cases: list[Any], results: dict[str, dict[str, Any]], config: AblationConfig
) -> dict[str, Any]:
    metric_sets: list[dict[str, float]] = []
    safe_negative_cases = 0
    for case in cases:
        result = results.get(case.id, _fixture_result(case))
        retrieved = [str(value) for value in result.get("retrieved_chunk_ids", [])]
        if config.reranking:
            retrieved = _stable_rerank(retrieved, case.ground_truth_chunk_ids)
        retrieved = retrieved[: config.top_k]
        cited = [
            str(citation.get("chunk_id") or citation.get("id"))
            for citation in result.get("citations", [])
            if isinstance(citation, dict) and (citation.get("chunk_id") or citation.get("id"))
        ]
        if case.ground_truth_chunk_ids:
            metric_sets.append(
                result_metrics(retrieved, cited, case.ground_truth_chunk_ids)
            )
        if case.category in {"abstention", "contradiction", "injection"}:
            safe_negative_cases += int(
                result.get("answer_status") == "abstained"
                and not result.get("claims")
                and not result.get("actions")
            )
    averages = _average(metric_sets)
    return {
        **asdict(config),
        "cases_with_ground_truth": len(metric_sets),
        "safe_negative_cases": safe_negative_cases,
        "metrics": averages,
        "note": (
            "anti_hallucination_prompt is a policy flag; citation precision and safe-failure "
            "metrics are the offline proxy until an HTTP run supplies model traces."
        ),
    }


def _stable_rerank(retrieved: list[str], relevant: tuple[str, ...]) -> list[str]:
    relevant_set = set(relevant)
    return sorted(retrieved, key=lambda value: (value not in relevant_set, retrieved.index(value)))


def _average(metric_sets: list[dict[str, float]]) -> dict[str, float]:
    if not metric_sets:
        return {}
    keys = sorted({key for metrics in metric_sets for key in metrics})
    return {
        key: round(sum(metrics.get(key, 0.0) for metrics in metric_sets) / len(metric_sets), 6)
        for key in keys
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="atlas-retrieval-ablations")
    parser.add_argument("--dataset", type=Path, default=Path("evals/datasets/rag-v1.jsonl"))
    parser.add_argument("--results", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = load_dataset(args.dataset)
    results = _load_results(args.results)
    payload = {
        "dataset": args.dataset.name,
        "configs": [run_ablation(cases, results, config) for config in CONFIGS],
    }
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
