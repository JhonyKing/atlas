from __future__ import annotations

import pytest

from atlas.agent.tools.read_only import ReadOnlyToolAdapters, bounded_result


@pytest.mark.asyncio
async def test_read_only_adapter_normalizes_evidence_and_artifacts() -> None:
    received: dict[str, object] = {}

    async def cited_answer(arguments: dict[str, object]) -> dict[str, object]:
        received.update(arguments)
        return {
            "status": "completed",
            "evidence_ids": ["ev-1", "ev-2"],
            "artifact_ids": ["answer-1"],
            "claim_count": 2,
        }

    adapters = ReadOnlyToolAdapters({"cited_answer": cited_answer})
    arguments = {"question": "How does LangGraph persist state?"}

    result = await adapters.execute("cited_answer", arguments)

    assert received == arguments
    assert arguments == {"question": "How does LangGraph persist state?"}
    assert result["status"] == "completed"
    assert result["evidence_ids"] == ("ev-1", "ev-2")
    assert result["artifact_ids"] == ("answer-1",)
    assert result["claim_count"] == 2


@pytest.mark.asyncio
async def test_missing_read_only_adapter_abstains_without_invoking_provider() -> None:
    adapters = ReadOnlyToolAdapters({})

    result = await adapters.execute("comparison", {"technologies": ["openai", "anthropic"]})

    assert result == bounded_result(status="abstained", reason="adapter_unavailable")


def test_private_or_unknown_handlers_cannot_be_registered() -> None:
    async def handler(_arguments: dict[str, object]) -> dict[str, object]:
        return {"status": "completed"}

    with pytest.raises(ValueError, match="read-only"):
        ReadOnlyToolAdapters({"private_delete": handler})
    with pytest.raises(ValueError, match="read-only"):
        ReadOnlyToolAdapters({"arbitrary_url": handler})


@pytest.mark.asyncio
async def test_adapter_failure_is_redacted_to_a_bounded_result() -> None:
    async def failing(_arguments: dict[str, object]) -> dict[str, object]:
        raise RuntimeError("provider secret should not be returned")

    result = await ReadOnlyToolAdapters({"daily_news": failing}).execute("daily_news", {})

    assert result["status"] == "failed"
    assert result["reason"] == "adapter_failed"
    assert "provider secret" not in repr(result)
