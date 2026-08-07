"""Batch evaluation for the deterministic model router."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from atlas.config import Settings
from atlas.models import ModelRouter, TaskSignals


def evaluate(path: Path) -> dict[str, object]:
    router = ModelRouter(Settings())
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    results = []
    for case in cases:
        selection = router.select(
            TaskSignals(
                kind=case["kind"],
                complexity=case["complexity"],
                freshness_required=case["freshness_required"],
                contradiction_detected=case["contradiction_detected"],
                report_depth=case["report_depth"],
            )
        )
        results.append(
            {
                "id": case["id"],
                "passed": selection.model == case["expected_model"]
                and selection.reasoning_effort == case["expected_effort"],
                "model": selection.model,
                "reasoning_effort": selection.reasoning_effort,
            }
        )
    return {
        "dataset": str(path),
        "total": len(results),
        "passed": sum(result["passed"] for result in results),
        "cases": results,
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
