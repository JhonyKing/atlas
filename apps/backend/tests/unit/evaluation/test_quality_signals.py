from evals.evaluators.quality_loop import (
    JudgeContract,
    OnlineSignals,
    evaluate_online_signals,
)


def test_judge_contract_requires_versioned_criteria_and_bias_controls() -> None:
    contract = JudgeContract("judge-v1", ("faithfulness", "relevance"), ("fixed rubric",))
    contract.validate()


def test_online_signals_report_security_and_anomaly_failures() -> None:
    passed, reasons = evaluate_online_signals(OnlineSignals(True, True, 1.5, 2, 0.1))
    assert not passed
    assert "security signal failed" in reasons
    assert "anomaly threshold exceeded" in reasons
