from __future__ import annotations

from typing import cast
from uuid import UUID, uuid4

from pydantic import SecretStr
from pytest import MonkeyPatch

from atlas.config import Settings
from atlas.observability import langsmith as langsmith_module
from atlas.observability.langsmith import (
    LangSmithTraceSink,
    NullTraceSink,
    sanitize_trace_payload,
)


class FakeLangSmithClient:
    def __init__(self) -> None:
        self.created: list[dict[str, object]] = []
        self.updated: list[dict[str, object]] = []

    def create_run(self, **payload: object) -> None:
        self.created.append(payload)

    def update_run(self, run_id: UUID, **payload: object) -> None:
        self.updated.append({"run_id": run_id, **payload})


def test_from_settings_keeps_sanitized_inputs_and_outputs_visible(
    monkeypatch: MonkeyPatch,
) -> None:
    client_options: dict[str, object] = {}

    class ConfiguredFakeLangSmithClient(FakeLangSmithClient):
        def __init__(self, **options: object) -> None:
            super().__init__()
            client_options.update(options)

    monkeypatch.setattr(langsmith_module, "Client", ConfiguredFakeLangSmithClient)
    sink = LangSmithTraceSink.from_settings(
        Settings(langsmith_tracing=True, langsmith_api_key=SecretStr("test-only-key"))
    )

    assert isinstance(sink, LangSmithTraceSink)
    assert client_options["hide_inputs"] is False
    assert client_options["hide_outputs"] is False


def test_langsmith_sink_sends_functional_payload_and_only_safe_metadata() -> None:
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
        inputs={
            "question": {"text": "How does LangSmith tracing work?"},
            "authorization": "Bearer must-not-leave",
        },
        tags=("answer", "es-MX"),
    )
    sink.end(
        handle,
        status="completed",
        fields={"citation_count": 2, "private_content": "must not leave process"},
        inputs={"evidence": [{"excerpt": "Retrieved evidence"}]},
        outputs={
            "answer": {"claims": [{"text": "Verified answer"}]},
            "verification": {"status": "completed"},
            "api_key": "lsv2_must-not-leave",
        },
    )

    assert len(client.created) == 1
    created = client.created[0]
    assert created["project_name"] == "atlas-tests"
    assert "private question" not in str(created)
    assert "private excerpt" not in str(created)
    assert "es-MX" in str(created)
    assert "gpt-5.6-luna" in str(created)
    metadata = cast(dict[str, object], cast(dict[str, object], created["extra"])["metadata"])
    assert metadata["locale"] == "es-MX"
    assert metadata["model"] == "gpt-5.6-luna"
    assert metadata["prompt_version"] == "cited-answer-v1"
    assert metadata["retrieval_version"] == "hybrid-v1"
    assert metadata["embedding_profile"] == "text-embedding-3-small:1536"
    assert metadata["application_version"] == "0.1.0"
    assert metadata["corpus_snapshot"] == "demo-unverified"
    assert created["tags"] == ["answer", "es-MX"]
    created_inputs = cast(dict[str, object], created["inputs"])
    assert created_inputs["question"] == {"text": "How does LangSmith tracing work?"}
    assert created_inputs["authorization"] == "[REDACTED]"
    assert len(client.updated) == 1
    assert client.updated[0]["inputs"] == {"evidence": [{"excerpt": "Retrieved evidence"}]}
    assert client.updated[0]["outputs"] == {
        "citation_count": 2,
        "answer": {"claims": [{"text": "Verified answer"}]},
        "verification": {"status": "completed"},
        "api_key": "[REDACTED]",
        "status": "completed",
    }


def test_trace_payload_redacts_nested_credentials_and_bounds_content() -> None:
    payload = sanitize_trace_payload(
        {
            "question": "q" * 4_100,
            "evidence": [
                {
                    "excerpt": "Safe evidence",
                    "headers": {"Authorization": "Bearer credential-value"},
                    "url": "https://example.test/?token=credential-value",
                }
            ],
            "password": "credential-value",
        }
    )

    assert str(payload["question"]).endswith("...[TRUNCATED]")
    assert payload["password"] == "[REDACTED]"
    serialized = repr(payload)
    assert "Safe evidence" in serialized
    assert "credential-value" not in serialized


def test_null_sink_is_safe_without_langsmith() -> None:
    sink = NullTraceSink()
    handle = sink.start("atlas.answer", request_id=uuid4(), run_id=uuid4())
    sink.end(handle, status="completed", fields={"secret": "never"})
    assert handle.active is False
