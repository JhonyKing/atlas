"""Provider-neutral structured graders and secret-free negative-case export."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from evals.evaluators.deterministic import EvaluationCase, evaluate_case
from evals.evaluators.report import evaluate_report


@dataclass(frozen=True, slots=True)
class StructuredGrade:
    grader: Literal["code", "model", "human"]
    score: float
    strengths: tuple[str, ...]
    weaknesses: tuple[str, ...]
    rationale: str


def grade_code(case: EvaluationCase, actual: dict[str, Any]) -> StructuredGrade:
    result = evaluate_case(case, actual)
    return StructuredGrade(
        grader="code",
        score=float(result.passed),
        strengths=("deterministic contract passed",) if result.passed else (),
        weaknesses=result.reasons,
        rationale="; ".join(result.reasons) or "all deterministic checks passed",
    )


def grade_model(*, score: float, strengths: list[str], weaknesses: list[str], rationale: str) -> StructuredGrade:
    return _grade("model", score, strengths, weaknesses, rationale)


def grade_human(*, score: float, strengths: list[str], weaknesses: list[str], rationale: str) -> StructuredGrade:
    return _grade("human", score, strengths, weaknesses, rationale)


def grade_report(case: dict[str, Any], report: dict[str, Any]) -> StructuredGrade:
    passed = evaluate_report(case, report)
    return StructuredGrade(
        grader="code",
        score=float(passed),
        strengths=("report contract passed",) if passed else (),
        weaknesses=() if passed else ("report schema, section or citation contract failed",),
        rationale="report contract passed" if passed else "report contract failed",
    )


def export_negative_cases(
    cases: list[EvaluationCase],
    actual: list[dict[str, Any]],
    output: str | Path,
    *,
    dataset_version: str,
    application_commit: str,
    corpus_snapshot: str,
) -> int:
    """Export only IDs, hashes, labels and reasons; omit question/answer/content fields."""

    rows: list[dict[str, Any]] = []
    for case, result in zip(cases, actual, strict=True):
        grade = grade_code(case, result)
        if grade.score >= 1:
            continue
        rows.append(
            {
                "id": case.id,
                "category": case.category,
                "locale": case.locale,
                "collection": case.collection,
                "question_sha256": hashlib.sha256(case.question.encode("utf-8")).hexdigest(),
                "ground_truth_chunk_ids": list(case.ground_truth_chunk_ids),
                "reasons": list(grade.weaknesses),
                "dataset_version": dataset_version,
                "application_commit": application_commit,
                "corpus_snapshot": corpus_snapshot,
            }
        )
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")
    return len(rows)


def _grade(grader: Literal["model", "human"], score: float, strengths: list[str], weaknesses: list[str], rationale: str) -> StructuredGrade:
    if not 0 <= score <= 1:
        raise ValueError("grade score must be between 0 and 1")
    return StructuredGrade(grader, score, tuple(strengths), tuple(weaknesses), rationale)


__all__ = ["StructuredGrade", "export_negative_cases", "grade_code", "grade_human", "grade_model", "grade_report"]
