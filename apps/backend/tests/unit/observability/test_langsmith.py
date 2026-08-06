from __future__ import annotations

from uuid import uuid4

from atlas.observability.langsmith import LangSmithTraceSink, NullTraceSink


class FakeLangSmithClient:
    def __init__(self) -> None:
        self.created: list[dict[str, object]] = []
        self.updated: list[dict[str, object]] = []

    def create_run(self, **payload: object) -> None:
        self.created.append(payload)

    def update_run(self, run_id, **payload: object) -> None:
        self.updated.append({"run_id": run_id, **payload})


def test_langsmith_sink_sends_only_safe_metadata() -> None:
    client = FakeLangSmithClient()
    sink = LangSmithTraceSink(client, project="atlas-tests")
    request_id = uuid4()
    handle = sink.start(
        "atlas.answer",
        request_id=request_id,
        run_id=uuid4(),
        fields={
            "locale": "es-MX",
            "model": "gpt-5.6-luna",
            "prompt_version": "cited-answer-v1",
            "retrieval_version": "hybrid-v1",
            "embedding_profile": "text-embedding-3-small:1536",
            "application_version": "0.1.0",
            "corpus_snapshot": "demo-unverified",
            "question": "private question",
            "evidence_excerpt": "private excerpt",
        },
        tags=("answer", "es-MX"),
    )
    sink.end(
        handle,
        status="completed",
        fields={"citation_count": 2, "private_content": "must not leave process"},
    )

    assert len(client.created) == 1
    created = client.created[0]
    assert created["project_name"] == "atlas-tests"
    assert "private question" not in str(created)
    assert "private excerpt" not in str(created)
    assert "es-MX" in str(created)
    assert "gpt-5.6-luna" in str(created)
    metadata = created["extra"]["metadata"]
    assert metadata["locale"] == "es-MX"
    assert metadata["model"] == "gpt-5.6-luna"
    assert metadata["prompt_version"] == "cited-answer-v1"
    assert metadata["retrieval_version"] == "hybrid-v1"
    assert metadata["embedding_profile"] == "text-embedding-3-small:1536"
    assert metadata["application_version"] == "0.1.0"
    assert metadata["corpus_snapshot"] == "demo-unverified"
    assert created["tags"] == ["answer", "es-MX"]
    assert len(client.updated) == 1
    assert client.updated[0]["outputs"] == {"status": "completed", "citation_count": 2}


def test_null_sink_is_safe_without_langsmith() -> None:
    sink = NullTraceSink()
    handle = sink.start("atlas.answer", request_id=uuid4(), run_id=uuid4())
    sink.end(handle, status="completed", fields={"secret": "never"})
    assert handle.active is False
