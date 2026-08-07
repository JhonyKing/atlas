from atlas.agent.checkpoints import InMemoryCheckpointRepository
from atlas.agent.orchestration import classify_question


def test_classification_and_checkpoint_summary_do_not_expose_secrets() -> None:
    classification = classify_question("What changed in Gemini?")
    assert "api_key" not in repr(classification).lower()
    assert InMemoryCheckpointRepository().redact_summary({"token": "secret", "count": 1}) == {
        "token": "[REDACTED]",
        "count": 1,
    }
