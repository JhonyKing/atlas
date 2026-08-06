from evals.evaluators.deterministic import load_dataset
from evals.retrieval_ablations import CONFIGS, run_ablation
from evals.run_offline import _fixture_result


def test_ablation_matrix_covers_required_retrieval_variants() -> None:
    assert {config.top_k for config in CONFIGS} == {4, 8, 10}
    assert any(config.reranking for config in CONFIGS)
    assert any(config.anti_hallucination_prompt for config in CONFIGS)
    assert all(config.retrieval == "hybrid" for config in CONFIGS)


def test_ablation_metrics_are_repeatable_for_fixture_results() -> None:
    cases = load_dataset("evals/datasets/rag-v1.jsonl")
    results = {case.id: _fixture_result(case) for case in cases}
    first = run_ablation(cases, results, CONFIGS[1])
    second = run_ablation(cases, results, CONFIGS[1])
    assert first == second
    assert first["cases_with_ground_truth"] > 0
    assert first["metrics"]["hit_at_8"] == 1.0
