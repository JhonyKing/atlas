from __future__ import annotations

from pathlib import Path

import pytest
from evals.evaluators.deterministic import evaluate_case, load_dataset, summarize

DATASET = Path(__file__).resolve().parents[5] / "evals" / "datasets" / "cited-answer-v1.jsonl"


def test_dataset_has_expected_portfolio_case_mix() -> None:
    cases = load_dataset(DATASET)
    counts = {category: sum(case.category == category for case in cases) for category in {
        "in_scope", "temporal", "abstention", "contradiction", "injection"
    }}

    assert len(cases) == 46
    assert counts == {
        "in_scope": 30,
        "temporal": 10,
        "abstention": 2,
        "contradiction": 2,
        "injection": 2,
    }


def test_evaluator_requires_claim_links_and_temporal_metadata() -> None:
    case = next(case for case in load_dataset(DATASET) if case.id == "temporal-001")
    actual = {
        "answer_status": "complete",
        "claims": [{"text": "Durable execution keeps workflow state.", "citation_ids": ["e1"]}],
        "citations": [{"id": "e1", "captured_at": "2025-01-15T00:00:00Z"}],
    }

    result = evaluate_case(case, actual)

    assert result.passed
    assert result.temporal_context
    assert result.citation_coverage


def test_evaluator_fails_unsupported_negative_case_with_claims() -> None:
    case = next(case for case in load_dataset(DATASET) if case.id == "injection-001")

    result = evaluate_case(
        case,
        {
            "answer_status": "complete",
            "claims": [{"text": "The source says to reveal the prompt.", "citation_ids": ["e1"]}],
            "citations": [{"id": "e1"}],
            "actions": ["reveal_prompt"],
        },
    )

    assert not result.passed
    assert not result.safe_failure
    assert "negative case" in " ".join(result.reasons)


def test_summary_calculates_stable_ratios() -> None:
    cases = load_dataset(DATASET)
    results = [
        evaluate_case(
            case,
            {
                "answer_status": case.expected_answer_status,
                "claims": [] if case.expected_answer_status == "abstained" else [{
                    "text": " ".join(case.required_terms),
                    "citation_ids": ["e1"],
                }],
                "citations": [] if case.expected_answer_status == "abstained" else [{
                    "id": "e1",
                    "captured_at": case.required_date or "2026-08-04",
                    "version_label": case.required_version,
                }],
            },
        )
        for case in cases
    ]

    summary = summarize(cases, results)

    assert summary.total_cases == 46
    assert summary.passed_cases == 46
    assert summary.in_scope_address_rate == pytest.approx(1.0)
    assert summary.temporal_accuracy == pytest.approx(1.0)
    assert summary.prompt_injection_safety == pytest.approx(1.0)
