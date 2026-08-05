"""Versioned offline/HTTP evaluation runner for the Plan Maestro harness."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

# Support both ``python -m evals.run_offline`` and direct execution from the
# repository root, which is useful for a portfolio quickstart.
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals.evaluators.deterministic import evaluate_case, load_dataset, summarize
from evals.evaluators.retrieval import extract_citation_chunk_ids, result_metrics


DEFAULT_DATASET = Path(__file__).parent / "datasets" / "rag-v1.jsonl"


def main() -> int:
    parser = argparse.ArgumentParser(prog="atlas-eval-offline")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--results", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--http", action="store_true", help="Call the API; network is opt-in.")
    parser.add_argument("--api-origin", default="http://127.0.0.1:8000")
    parser.add_argument("--corpus-snapshot", default="unknown")
    args = parser.parse_args()
    cases = load_dataset(args.dataset)
    provided = _load_results(args.results) if args.results else {}
    if args.http:
        provided.update(_run_http(cases, args.api_origin))
    actual = [provided.get(case.id, _fixture_result(case)) for case in cases]
    evaluations = [evaluate_case(case, result) for case, result in zip(cases, actual, strict=True)]
    summary = summarize(cases, evaluations)
    payload = {
        "dataset": args.dataset.name,
        "dataset_version": "rag-v1",
        "execution_mode": "http" if args.http else "offline-fixture",
        "application_commit": _git_revision(),
        "corpus_snapshot": args.corpus_snapshot,
        "summary": asdict(summary),
        "retrieval": _retrieval_summary(cases, actual),
        "cases": [{"id": result.case_id, "passed": result.passed, "reasons": result.reasons} for result in evaluations],
    }
    serialized = json.dumps(payload, indent=2, sort_keys=True, default=list)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0


def _load_results(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    results: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            raw = json.loads(line)
            results[str(raw["id"])] = raw
    return results


def _run_http(cases: list[Any], api_origin: str) -> dict[str, dict[str, Any]]:
    import httpx

    results: dict[str, dict[str, Any]] = {}
    with httpx.Client(base_url=api_origin, timeout=30.0) as client:
        for index, case in enumerate(cases):
            response = client.post(
                "/v1/answers",
                headers={"Idempotency-Key": f"eval-{case.id}-{index:04d}"},
                json={"question": case.question, "product": case.collection, "language": case.locale},
            )
            response.raise_for_status()
            results[case.id] = _parse_sse(response.text)
    return results


def _parse_sse(text: str) -> dict[str, Any]:
    payload: dict[str, Any] = {"answer_status": "abstained", "claims": [], "citations": [], "actions": []}
    for line in text.splitlines():
        if not line.startswith("data: "):
            continue
        event = json.loads(line[6:])
        if event.get("stage") in {"completed", "abstained"}:
            payload.update(
                answer_status="abstained" if event["stage"] == "abstained" else event.get("answer_status"),
                claims=event.get("claims", []),
                citations=event.get("citations", []),
            )
    return payload


def _fixture_result(case: Any) -> dict[str, Any]:
    if case.expected_answer_status == "abstained":
        return {"answer_status": "abstained", "claims": [], "citations": [], "actions": []}
    citation_id = f"fixture-{case.id}"
    return {
        "answer_status": case.expected_answer_status,
        "claims": [{"text": " ".join(case.required_terms), "citation_ids": [citation_id]}],
        "citations": [{
            "id": citation_id,
            "chunk_id": case.ground_truth_chunk_ids[0] if case.ground_truth_chunk_ids else citation_id,
            "captured_at": case.required_date or "2026-08-04T00:00:00Z",
            "version_label": case.required_version,
        }],
        "retrieved_chunk_ids": list(case.ground_truth_chunk_ids),
        "actions": [],
    }


def _retrieval_summary(cases: list[Any], results: list[dict[str, Any]]) -> dict[str, float | int]:
    metric_sets: list[dict[str, float]] = []
    for case, result in zip(cases, results, strict=True):
        if not case.ground_truth_chunk_ids:
            continue
        captured_at = next(
            (
                citation.get("captured_at")
                for citation in result.get("citations", [])
                if isinstance(citation, dict) and citation.get("captured_at")
            ),
            None,
        )
        metric_sets.append(
            result_metrics(
                [str(chunk_id) for chunk_id in result.get("retrieved_chunk_ids", [])],
                extract_citation_chunk_ids(result),
                case.ground_truth_chunk_ids,
                captured_at=captured_at,
                evaluated_at="2026-08-05T00:00:00Z" if captured_at else None,
            )
        )
    if not metric_sets:
        return {"cases_with_ground_truth": 0}
    keys = sorted({key for metric_set in metric_sets for key in metric_set})
    return {
        "cases_with_ground_truth": len(metric_sets),
        **{
            key: sum(metric_set.get(key, 0.0) for metric_set in metric_sets) / len(metric_sets)
            for key in keys
        },
    }


def _git_revision() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
