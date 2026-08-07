from atlas.slo import SLOMeasurement, evaluate_gate


def test_slo_gate_passes_only_with_complete_measurement() -> None:
    passed, failures = evaluate_gate(
        SLOMeasurement(0.999, 0.001, 8, 1, 120, 0.97, 1, 2)
    )
    assert passed is True
    assert failures == ()


def test_slo_gate_fails_closed_for_missing_or_regressed_metrics() -> None:
    passed, failures = evaluate_gate(
        SLOMeasurement(None, 0.02, 13, None, None, 0.90, 3, 2)
    )
    assert passed is False
    assert "availability missing" in failures
    assert "cost budget exceeded" in failures
