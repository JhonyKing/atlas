from __future__ import annotations

import json

import httpx
import pytest
from openai import AsyncOpenAI

from atlas.agent.tools.registry import ToolCatalog
from atlas.providers.openai_agent_planner import OpenAIAgentPlannerAdapter


def _response_payload() -> dict[str, object]:
    return {
        "id": "resp_plan_123",
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
                "id": "msg_plan_123",
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps(
                            {
                                "steps": [
                                    {
                                        "tool_id": "cited_answer",
                                        "tool_version": "1.0.0",
                                        "arguments": {
                                            "question": "How does LangGraph persist state?"
                                        },
                                        "dependencies": [],
                                        "expected_output": "tool_result",
                                    }
                                ]
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
        "usage": None,
        "metadata": {},
    }


@pytest.mark.asyncio
async def test_planner_adapter_sends_luna_structured_proposal_contract() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=_response_payload(), headers={"x-request-id": "req_plan"})

    client = AsyncOpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    adapter = OpenAIAgentPlannerAdapter(
        client=client,
        safety_identifier="d" * 64,
        max_retries=0,
        retry_delay=0,
    )
    try:
        proposal = await adapter.propose(
            "How does LangGraph persist state?", ToolCatalog.default(), locale="en-US"
        )
    finally:
        await client.close()

    body = json.loads(requests[0].content)
    assert body["model"] == "gpt-5.6-luna"
    assert body["store"] is False
    assert body["safety_identifier"] == "d" * 64
    assert "How does LangGraph persist state?" in body["input"]
    assert proposal.steps[0].tool_id == "cited_answer"
    assert adapter.last_response_id == "resp_plan_123"
