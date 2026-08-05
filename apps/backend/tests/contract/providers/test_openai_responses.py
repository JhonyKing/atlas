import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

import httpx
import pytest
from openai import AsyncOpenAI
from pydantic import HttpUrl

from atlas.domain import Evidence, Question, SourceType
from atlas.providers.openai_responses import (
    OpenAIResponsesAdapter,
    ProviderAdapterError,
    derive_safety_identifier,
)

NOW = datetime(2026, 8, 4, 12, 0, tzinfo=UTC)
EVIDENCE_ID = UUID("0198e4d5-7c4a-7c3e-8f0b-8c5c4d2e1f01")


def sample_evidence() -> Evidence:
    return Evidence(
        id=EVIDENCE_ID,
        source_title="Official docs",
        publisher="Example",
        canonical_url=HttpUrl("https://example.com/docs"),
        excerpt="A checkpointer saves graph state at super-step boundaries.",
        captured_at=NOW,
        source_type=SourceType.DOCUMENTATION,
    )


def response_payload() -> dict[str, object]:
    return {
        "id": "resp_123",
        "object": "response",
        "created_at": 1785844800,
        "status": "completed",
        "error": None,
        "incomplete_details": None,
        "instructions": None,
        "max_output_tokens": None,
        "model": "gpt-5.6-luna",
        "output": [
            {
                "id": "msg_123",
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps(
                            {
                                "answer_status": "complete",
                                "claims": [
                                    {
                                        "id": str(uuid4()),
                                        "ordinal": 0,
                                        "text": "A checkpointer saves graph state.",
                                        "type": "factual",
                                        "citation_ids": [str(uuid4())],
                                    }
                                ],
                                "evidence_ids": [str(EVIDENCE_ID)],
                                "limitations": [],
                            }
                        ),
                        "annotations": [],
                    }
                ],
            }
        ],
        "parallel_tool_calls": False,
        "previous_response_id": None,
        "reasoning": {"effort": "medium", "summary": None},
        "store": False,
        "temperature": None,
        "text": {"format": {"type": "text"}, "verbosity": "medium"},
        "tool_choice": "auto",
        "tools": [],
        "top_p": 1,
        "truncation": "disabled",
        "usage": {
            "input_tokens": 120,
            "output_tokens": 80,
            "total_tokens": 200,
            "input_tokens_details": {"cached_tokens": 10},
            "output_tokens_details": {"reasoning_tokens": 20},
        },
        "metadata": {},
    }


@pytest.mark.asyncio
async def test_adapter_sends_luna_contract_and_parses_structured_draft() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json=response_payload(),
            headers={"x-request-id": "req_123"},
        )

    client = AsyncOpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    adapter = OpenAIResponsesAdapter(client=client, safety_identifier="a" * 64, retry_delay=0)

    try:
        draft = await adapter.generate(
            Question(text="When does LangGraph need a checkpointer?"),
            [sample_evidence()],
        )
    finally:
        await client.close()

    body = json.loads(requests[0].content)
    assert body["model"] == "gpt-5.6-luna"
    assert body["store"] is False
    assert body["reasoning"] == {"effort": "medium", "context": "current_turn"}
    assert body["safety_identifier"] == "a" * 64
    assert "previous_response_id" not in body
    assert draft.answer_status.value == "complete"
    assert draft.evidence_ids == [EVIDENCE_ID]
    assert adapter.last_telemetry is not None
    assert adapter.last_telemetry.response_id == "resp_123"
    assert adapter.last_telemetry.input_tokens == 120
    assert adapter.last_telemetry.reasoning_tokens == 20


def test_safety_identifier_is_hmac_and_never_the_raw_visitor_key() -> None:
    identifier = derive_safety_identifier("local-secret", "visitor-cookie-value")

    assert len(identifier) == 64
    assert identifier != "visitor-cookie-value"
    assert identifier == derive_safety_identifier("local-secret", "visitor-cookie-value")


@pytest.mark.asyncio
async def test_adapter_retries_one_transient_failure_with_bounded_attempts() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(503, json={"error": {"message": "temporary"}})
        return httpx.Response(200, json=response_payload())

    client = AsyncOpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    adapter = OpenAIResponsesAdapter(
        client=client,
        safety_identifier="b" * 64,
        max_retries=1,
        retry_delay=0,
    )
    try:
        await adapter.generate(Question(text="What is a checkpointer?"), [sample_evidence()])
    finally:
        await client.close()

    assert attempts == 2


@pytest.mark.asyncio
async def test_adapter_redacts_provider_error_and_stops_after_retry_budget() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": {"message": "secret provider detail"}})

    client = AsyncOpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    adapter = OpenAIResponsesAdapter(
        client=client,
        safety_identifier="c" * 64,
        max_retries=1,
        retry_delay=0,
    )
    try:
        with pytest.raises(ProviderAdapterError, match="provider request failed") as error:
            await adapter.generate(Question(text="What is a checkpointer?"), [sample_evidence()])
    finally:
        await client.close()

    assert "secret provider detail" not in str(error.value)
