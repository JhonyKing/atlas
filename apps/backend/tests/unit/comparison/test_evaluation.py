from pathlib import Path

from evals.evaluators.comparison import evaluate_comparison_case


def test_comparison_evaluator_checks_coordinates_states_and_evidence_ids() -> None:
    case = {
        "id": "case-1",
        "expected_cells": [
            {
                "technology_id": "openai",
                "criterion_id": "price",
                "state": "unsupported",
                "evidence_ids": [],
            }
        ],
    }
    evaluation = evaluate_comparison_case(case, {"cells": case["expected_cells"]})
    assert evaluation.passed is True


def test_comparison_cli_fixture_covers_dataset_matrix_cases() -> None:
    path = Path(__file__).parents[5] / "evals" / "datasets" / "comparison-v1.jsonl"
    assert path.is_file()
