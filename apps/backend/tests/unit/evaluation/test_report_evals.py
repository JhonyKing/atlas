from pathlib import Path

from evals.evaluators.report import evaluate_report, load_report_cases


def test_report_eval_dataset_is_versioned_and_validated() -> None:
    cases = load_report_cases(Path(__file__).parents[5] / "evals" / "datasets" / "report-v1.jsonl")
    assert {case["id"] for case in cases} == {"report-en-comparison", "report-es-comparison"}
    english = {
        "citations": [{"citation_id": "E1", "excerpt": "Original evidence excerpt"}],
        "sections": [
            {"title": title, "citation_ids": ["E1"], "is_factual": True}
            for title in ["Executive summary", "Comparison matrix", "Limitations"]
        ]
        + [{"title": "References", "citation_ids": ["E1"], "is_factual": False}],
    }
    spanish = {**english, "sections": [
        {"title": title, "citation_ids": ["E1"], "is_factual": True}
        for title in ["Resumen ejecutivo", "Matriz de comparación", "Limitaciones"]
    ] + [{"title": "Referencias", "citation_ids": ["E1"], "is_factual": False}]}
    assert evaluate_report(cases[0], english)
    assert evaluate_report(cases[1], spanish)
