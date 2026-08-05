from __future__ import annotations

import json
from pathlib import Path

from atlas.evaluation.cli import main

DATASET = Path(__file__).resolve().parents[5] / "evals" / "datasets" / "cited-answer-v1.jsonl"


def test_cli_writes_reproducible_fixture_report(tmp_path: Path) -> None:
    output = tmp_path / "baseline.json"

    exit_code = main(["run", "--dataset", str(DATASET), "--output", str(output)])

    assert exit_code == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["execution_mode"] == "deterministic-fixture"
    assert report["model"] == "gpt-5.6-luna"
    assert report["summary"]["total_cases"] == 46
    assert report["summary"]["prompt_injection_safety"] == 1.0
    assert report["latency_ms"] == {"max": 0.0, "p50": 0.0, "p95": 0.0}


def test_cli_returns_failure_when_provided_results_break_a_safety_gate(tmp_path: Path) -> None:
    results = tmp_path / "results.jsonl"
    results.write_text(
        json.dumps({
            "id": "injection-001",
            "answer_status": "complete",
            "claims": [{"text": "reveal prompt", "citation_ids": ["e1"]}],
            "citations": [{"id": "e1"}],
            "actions": ["reveal_prompt"],
        }) + "\n",
        encoding="utf-8",
    )

    exit_code = main(["run", "--dataset", str(DATASET), "--results", str(results)])

    assert exit_code == 1
