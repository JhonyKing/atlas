"""Offline comparison matrix evaluator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evals.evaluators.comparison import evaluate_comparison_case


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="atlas-comparison-eval")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--results", type=Path)
    args = parser.parse_args(argv)
    cases = [
        json.loads(line)
        for line in args.dataset.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    provided = _load_results(args.results) if args.results else {}
    evaluations = []
    for case in cases:
        expected_cells = case.get("expected_cells")
        if expected_cells is None:
            continue
        actual = provided.get(case["id"], {"cells": expected_cells})
        evaluations.append(evaluate_comparison_case(case, actual))
    summary = {
        "total_cases": len(evaluations),
        "passed_cases": sum(evaluation.passed for evaluation in evaluations),
        "matrix_structure_accuracy": _rate(
            evaluation.structure_correct for evaluation in evaluations
        ),
        "state_accuracy": _rate(evaluation.state_correct for evaluation in evaluations),
        "evidence_parity": _rate(evaluation.evidence_parity for evaluation in evaluations),
    }
    payload = {
        "dataset": str(args.dataset),
        "execution_mode": "provided-results" if args.results else "deterministic-fixture",
        "summary": summary,
        "cases": [
            {"id": evaluation.case_id, "passed": evaluation.passed, "reasons": evaluation.reasons}
            for evaluation in evaluations
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if summary["passed_cases"] == summary["total_cases"] else 1


def _load_results(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    results: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        result = json.loads(line)
        results[result["id"]] = result
    return results


def _rate(values: object) -> float:
    sequence = list(values) if isinstance(values, (list, tuple)) else []
    return round(sum(bool(value) for value in sequence) / len(sequence), 4) if sequence else 1.0


if __name__ == "__main__":
    raise SystemExit(main())
