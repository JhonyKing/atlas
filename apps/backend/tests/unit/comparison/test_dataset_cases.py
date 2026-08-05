import json
from pathlib import Path


def test_comparison_dataset_has_deterministic_two_and_three_technology_cases() -> None:
    path = Path(__file__).parents[5] / "evals" / "datasets" / "comparison-v1.jsonl"
    cases = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    matrix_cases = {case["id"]: case for case in cases if "expected_cells" in case}

    assert len(cases) >= 20
    assert len(matrix_cases) >= 16
    assert len(matrix_cases["two-tech-capability"]["technologies"]) == 2
    assert len(matrix_cases["three-tech-price-gap"]["technologies"]) == 3
    for case in matrix_cases.values():
        assert all("state" in cell and "evidence_ids" in cell for cell in case["expected_cells"])
