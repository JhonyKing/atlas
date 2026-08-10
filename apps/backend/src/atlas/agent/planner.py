"""Provider-neutral planner seam with GPT-5.6 Luna as the default model label."""

from __future__ import annotations

from atlas.agent.planning import AgentPlan, proposal_for_request, validate_plan
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import Locale, ToolCallRequest
from atlas.providers.openai_responses import ProviderAdapterError
from atlas.providers.ports import AgentPlanProvider


class AgentPlanner:
    def __init__(
        self,
        catalog: ToolCatalog,
        *,
        model: str = "gpt-5.6-luna",
        proposal_provider: AgentPlanProvider | None = None,
    ) -> None:
        self.catalog = catalog
        self.model = model
        self.proposal_provider = proposal_provider

    def propose(self, request: str, *, locale: Locale = "en-US") -> AgentPlan:
        """Return the deterministic local proposal for synchronous callers."""

        return self._validate(
            request,
            locale,
            proposal_for_request(request, locale=locale),
        )

    async def propose_async(self, request: str, *, locale: Locale = "en-US") -> AgentPlan:
        """Use the typed provider when configured, with a bounded fallback on outages."""

        if self.proposal_provider is None:
            return self.propose(request, locale=locale)
        try:
            proposal = await self.proposal_provider.propose(
                request,
                self.catalog,
                locale=locale,
            )
        except ProviderAdapterError:
            return self.propose(request, locale=locale)
        return self._validate(request, locale, tuple(proposal.steps))

    def _validate(
        self,
        request: str,
        locale: Locale,
        steps: tuple[ToolCallRequest, ...],
    ) -> AgentPlan:
        return validate_plan(
            catalog=self.catalog,
            request=request,
            locale=locale,
            steps=tuple(steps),
            model_label=self.model,
        )
