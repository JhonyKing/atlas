"""Opt-in LangSmith dataset/evaluation linkage for the Plan Maestro harness.

The default command is a dry run. Network access, dataset writes and API calls
only happen when ``--execute`` is supplied together with ``LANGSMITH_API_KEY``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals.evaluators.deterministic import EvaluationCase, evaluate_case, load_dataset
from evals.run_offline import _git_revision, _parse_sse


DEFAULT_DATASET = Path(__file__).parent / "datasets" / "rag-v1.jsonl"
DEFAULT_DATASET_NAME = "atlas-rag-v1"


def main() -> int:
    parser = argparse.ArgumentParser(prog="atlas-eval-langsmith")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--dataset-name", default=DEFAULT_DATASET_NAME)
    parser.add_argument("--api-origin", default="http://127.0.0.1:8000")
    parser.add_argument("--corpus-snapshot", default="unknown")
    parser.add_argument("--project", default=os.getenv("LANGSMITH_PROJECT", "atlas-ai"))
    parser.add_argument("--max-concurrency", type=int, default=2)
    parser.add_argument("--execute", action="store_true", help="Enable LangSmith and API network calls.")
    args = parser.parse_args()

    cases = load_dataset(args.dataset)
    print(
        f"dataset={args.dataset.name} cases={len(cases)} project={args.project} "
        f"mode={'execute' if args.execute else 'dry-run'}"
    )
    if not args.execute:
        print("dry-run: no LangSmith dataset, backend request, or model call was made")
        return 0

    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        raise SystemExit("LANGSMITH_API_KEY is required for --execute and is never printed")

    from langsmith import Client

    client = Client(
        api_url=os.getenv("LANGSMITH_ENDPOINT") or None,
        api_key=api_key,
        workspace_id=os.getenv("LANGSMITH_WORKSPACE_ID") or None,
        hide_inputs=True,
        hide_outputs=True,
    )
    dataset = _get_or_create_dataset(client, args.dataset_name, cases)
    _upsert_examples(client, dataset.id, cases)
    result = client.evaluate(
        _http_target(args.api_origin),
        data=dataset.name,
        evaluators=[_langsmith_evaluator(cases)],
        metadata={
            "dataset_version": "rag-v1",
            "application_commit": _git_revision(),
            "corpus_snapshot": args.corpus_snapshot,
            "project": args.project,
        },
        experiment_prefix=f"atlas-rag-v1-{_git_revision()}",
        max_concurrency=args.max_concurrency,
        blocking=True,
    )
    print(f"LangSmith evaluation completed: {result}")
    return 0


def _get_or_create_dataset(client: Any, name: str, cases: list[EvaluationCase]) -> Any:
    existing = next(iter(client.list_datasets(dataset_name=name, limit=1)), None)
    if existing is not None:
        return existing
    return client.create_dataset(
        name,
        description="ATLAS Plan Maestro RAG evaluation dataset (60 versioned cases).",
        inputs_schema={"type": "object"},
        outputs_schema={"type": "object"},
        metadata={"dataset_version": "rag-v1", "case_count": len(cases)},
    )


def _upsert_examples(client: Any, dataset_id: Any, cases: list[EvaluationCase]) -> None:
    examples = [
        {
            "inputs": {
                "case_id": case.id,
                "question": case.question,
                "collection": case.collection,
                "language": case.locale,
            },
            "outputs": {
                "answer_status": case.expected_answer_status,
                "required_terms": list(case.required_terms),
                "min_citations": case.min_citations,
                "required_date": case.required_date,
                "required_version": case.required_version,
            },
        }
        for case in cases
    ]
    client.create_examples(dataset_id=dataset_id, examples=examples, max_concurrency=2)


def _http_target(api_origin: str):
    import httpx

    def target(inputs: dict[str, Any]) -> dict[str, Any]:
        with httpx.Client(base_url=api_origin, timeout=30.0) as client:
            response = client.post(
                "/v1/answers",
                headers={"Idempotency-Key": f"eval-{inputs['case_id']}"},
                json={
                    "question": inputs["question"],
                    "product": inputs["collection"],
                    "language": inputs["language"],
                },
            )
            response.raise_for_status()
            return _parse_sse(response.text)

    return target


def _langsmith_evaluator(cases: list[EvaluationCase]):
    by_id = {case.id: case for case in cases}

    def evaluator(run: Any, example: Any) -> dict[str, Any]:
        inputs = _value(run, "inputs") or {}
        outputs = _value(run, "outputs") or {}
        case = by_id[str(inputs.get("case_id"))]
        evaluation = evaluate_case(case, outputs)
        return {
            "key": "case_passed",
            "score": int(evaluation.passed),
            "comment": "; ".join(evaluation.reasons) or "all deterministic checks passed",
        }

    return evaluator


def _value(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


if __name__ == "__main__":
    raise SystemExit(main())
