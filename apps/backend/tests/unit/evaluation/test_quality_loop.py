from evals.evaluators.quality_loop import (
    QualityGate,
    evaluate_gate,
    evaluate_quality_case,
    safe_trace_tags,
)


def test_quality_case_reports_link_and_duplicate_failures() -> None:
    result = evaluate_quality_case(
        "case-1",
        {
            "claims": [{"citation_ids": ["a", "missing"]}],
            "citations": [{"id": "a"}, {"id": "a"}],
        },
    )
    assert not result.passed
    assert "citation link integrity failed" in result.reasons
    assert "duplicate citation IDs" in result.reasons


def test_quality_gate_fails_closed_and_trace_tags_redact_content() -> None:
    passed, reasons = evaluate_gate(QualityGate(0.90, True, 2, 1, 13))
    assert not passed
    assert "cost budget exceeded" in reasons
    tags = safe_trace_tags({"model_version": "m1", "prompt": "private question"})
    assert tags["prompt"] == "[REDACTED]"
