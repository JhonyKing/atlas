from atlas.config import Settings
from atlas.models import ModelRouter, TaskSignals


def test_luna_is_the_default_and_effort_is_signal_driven() -> None:
    selection = ModelRouter(Settings()).select(
        TaskSignals(kind="answer", complexity="low")
    )
    assert selection.model == "gpt-5.6-luna"
    assert selection.reasoning_effort == "low"


def test_contradiction_uses_high_reasoning_and_unknown_model_is_rejected() -> None:
    selection = ModelRouter(Settings()).select(TaskSignals(contradiction_detected=True))
    assert selection.reasoning_effort == "high"
    settings = Settings(atlas_answer_model="not-approved")
    try:
        ModelRouter(settings).select(TaskSignals())
    except ValueError as exc:
        assert "approved" in str(exc)
    else:
        raise AssertionError("unknown model should be rejected")
