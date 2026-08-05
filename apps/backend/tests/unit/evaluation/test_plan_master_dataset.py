from pathlib import Path

from evals.evaluators.deterministic import load_dataset

DATASET = Path(__file__).resolve().parents[5] / "evals" / "datasets" / "rag-v1.jsonl"


def test_plan_master_dataset_has_sixty_cases_and_required_metadata() -> None:
    cases = load_dataset(DATASET)

    assert len(cases) == 60
    assert any(case.question.startswith("¿") for case in cases)
    assert sum(case.category in {"abstention", "contradiction", "injection"} for case in cases) >= 9
    assert sum(case.category == "multi_hop" for case in cases) >= 2
    assert sum(case.category == "ocr" for case in cases) >= 1
    assert all(case.collection for case in cases)
    assert all(case.locale in {"en-US", "es-MX"} for case in cases)
