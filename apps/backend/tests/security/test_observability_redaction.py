"""Hosted trace payloads expose evaluation content while recursively redacting credentials."""

from uuid import uuid4

from atlas.observability.langsmith import LangSmithTraceSink


class FakeClient:
    def __init__(self) -> None:
        self.created: dict[str, object] = {}
        self.updated: dict[str, object] = {}

    def create_run(self, **kwargs: object) -> None:
        self.created = kwargs

    def update_run(self, _run_id: object, **kwargs: object) -> None:
        self.updated = kwargs


def test_langsmith_trace_does_not_forward_secret_or_private_content() -> None:
    client = FakeClient()
    sink = LangSmithTraceSink(client, project="atlas-test")
    request_id = uuid4()
    handle = sink.start(
        "answer",
        request_id=request_id,
        run_id=uuid4(),
        fields={"api_key": "sk-never-forward-this", "private_document": "sensitive"},
        inputs={
            "question": "Visible evaluation question",
            "evidence": {"excerpt": "Visible evidence"},
            "headers": {"authorization": "Bearer never-forward-this"},
        },
    )
    sink.end(
        handle,
        status="abstained",
        fields={"session_token": "secret"},
        outputs={
            "answer": "Visible generated answer",
            "verification": {"status": "abstained", "api_key": "sk-never-forward-this"},
        },
    )
    serialized = repr((client.created, client.updated))
    assert "sk-never-forward-this" not in serialized
    assert "sensitive" not in serialized
    assert "never-forward-this" not in serialized
    assert "Visible evaluation question" in serialized
    assert "Visible evidence" in serialized
    assert "Visible generated answer" in serialized
