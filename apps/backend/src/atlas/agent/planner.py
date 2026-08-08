"""Provider-neutral planner seam with GPT-5.6 Luna as the default model label."""

from __future__ import annotations

from atlas.agent.planning import AgentPlan, proposal_for_request, validate_plan
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import Locale


class AgentPlanner:
    def __init__(self, catalog: ToolCatalog, *, model: str = "gpt-5.6-luna") -> None:
        self.catalog = catalog
        self.model = model

    def propose(self, request: str, *, locale: Locale = "en-US") -> AgentPlan:
        proposed = proposal_for_request(request, locale=locale)
        return validate_plan(
            catalog=self.catalog,
            request=request,
            locale=locale,
            steps=proposed,
            model_label=self.model,
        )
