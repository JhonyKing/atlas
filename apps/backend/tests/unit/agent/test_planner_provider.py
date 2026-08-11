from __future__ import annotations

import pytest

from atlas.agent.planner import AgentPlanner
from atlas.agent.planning import PlanValidationError
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import Locale, ToolCallRequest
from atlas.providers.openai_responses import ProviderAdapterError
from atlas.providers.ports import AgentPlanProposal


class FakeProposalProvider:
    def __init__(
        self,
        proposal: AgentPlanProposal | None = None,
        error: Exception | None = None,
    ) -> None:
        self.proposal = proposal
        self.error = error
        self.calls = 0

    async def propose(
        self,
        request: str,
        catalog: ToolCatalog,
        *,
        locale: Locale,
    ) -> AgentPlanProposal:
        del request, catalog, locale
        self.calls += 1
        if self.error is not None:
            raise self.error
        assert self.proposal is not None
        return self.proposal


@pytest.mark.asyncio
async def test_planner_uses_typed_provider_proposal_and_luna_label() -> None:
    provider = FakeProposalProvider(
        AgentPlanProposal(
            steps=[
                ToolCallRequest(
                    tool_id="cited_answer",
                    tool_version="1.0.0",
                    arguments={"question": "How does LangGraph persist state?"},
                )
            ]
        )
    )
    planner = AgentPlanner(ToolCatalog.default(), proposal_provider=provider)

    plan = await planner.propose_async("How does LangGraph persist state?")

    assert provider.calls == 1
    assert plan.model_label == "gpt-5.6-luna"
    assert plan.steps[0].tool_id == "cited_answer"
    assert plan.steps[0].arguments["question"] == "How does LangGraph persist state?"


@pytest.mark.asyncio
async def test_invalid_provider_tool_fails_closed_instead_of_falling_back() -> None:
    provider = FakeProposalProvider(
        AgentPlanProposal(
            steps=[ToolCallRequest(tool_id="not_allowlisted", tool_version="1.0.0")]
        )
    )
    planner = AgentPlanner(ToolCatalog.default(), proposal_provider=provider)

    with pytest.raises(PlanValidationError, match="unknown tool"):
        await planner.propose_async("Do something")


@pytest.mark.asyncio
async def test_provider_transport_failure_uses_bounded_deterministic_fallback() -> None:
    provider = FakeProposalProvider(error=ProviderAdapterError("provider request failed"))
    planner = AgentPlanner(ToolCatalog.default(), proposal_provider=provider)

    plan = await planner.propose_async("What changed in Gemini?")

    assert provider.calls == 1
    assert plan.steps[0].tool_id == "cited_answer"
    assert plan.steps[0].arguments["question"] == "What changed in Gemini?"


def test_sync_planner_api_remains_deterministic_without_a_provider() -> None:
    planner = AgentPlanner(ToolCatalog.default())

    plan = planner.propose("How does LangGraph persist state?")

    assert plan.steps[0].tool_id == "cited_answer"
