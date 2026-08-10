"""OpenAI Responses adapter for bounded ATLAS agent-plan proposals."""

from __future__ import annotations

import asyncio
import re
from typing import Literal

from openai import APIConnectionError, APIStatusError, AsyncOpenAI
from openai.types.shared_params.reasoning import Reasoning

from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import Locale
from atlas.providers.openai_responses import (
    _RETRYABLE_STATUS_CODES,
    MODEL_ID,
    ProviderAdapterError,
)
from atlas.providers.ports import AgentPlanProposal
from atlas.providers.prompts.agent_planner import (
    AGENT_PLANNER_INSTRUCTIONS,
    build_agent_planner_input,
)

REASONING_EFFORT: Literal["medium"] = "medium"
_SAFETY_IDENTIFIER_RE = re.compile(r"^[0-9a-f]{64}$")


class OpenAIAgentPlannerAdapter:
    """Structured planner adapter; output is still untrusted until plan validation."""

    def __init__(
        self,
        *,
        client: AsyncOpenAI,
        safety_identifier: str,
        model: str = MODEL_ID,
        max_retries: int = 2,
        retry_delay: float = 0.25,
    ) -> None:
        if not _SAFETY_IDENTIFIER_RE.fullmatch(safety_identifier):
            raise ValueError("safety_identifier must be a 64-character lowercase HMAC digest")
        if max_retries < 0:
            raise ValueError("max_retries must not be negative")
        if retry_delay < 0:
            raise ValueError("retry_delay must not be negative")
        self._client = client
        self._safety_identifier = safety_identifier
        self._model = model
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self.last_response_id: str | None = None

    async def propose(
        self,
        request: str,
        catalog: ToolCatalog,
        *,
        locale: Locale,
    ) -> AgentPlanProposal:
        input_text = build_agent_planner_input(request, catalog, locale)
        for attempt in range(self._max_retries + 1):
            try:
                reasoning: Reasoning = {"effort": REASONING_EFFORT, "context": "current_turn"}
                response = await self._client.responses.parse(
                    model=self._model,
                    instructions=AGENT_PLANNER_INSTRUCTIONS,
                    input=input_text,
                    reasoning=reasoning,
                    safety_identifier=self._safety_identifier,
                    store=False,
                    text_format=AgentPlanProposal,
                )
            except (APIConnectionError, APIStatusError) as exc:
                retryable = self._is_retryable(exc)
                if retryable and attempt < self._max_retries:
                    if self._retry_delay:
                        await asyncio.sleep(self._retry_delay * (2**attempt))
                    continue
                raise ProviderAdapterError("provider request failed", retryable=retryable) from exc
            except Exception as exc:
                if attempt < self._max_retries:
                    if self._retry_delay:
                        await asyncio.sleep(self._retry_delay * (2**attempt))
                    continue
                raise ProviderAdapterError("provider response could not be parsed") from exc

            parsed = response.output_parsed
            if not isinstance(parsed, AgentPlanProposal):
                raise ProviderAdapterError("provider response did not contain a structured plan")
            self.last_response_id = getattr(response, "id", None)
            return parsed

        raise AssertionError("retry loop must return or raise")

    @staticmethod
    def _is_retryable(error: APIConnectionError | APIStatusError) -> bool:
        if isinstance(error, APIConnectionError):
            return True
        return error.status_code in _RETRYABLE_STATUS_CODES


__all__ = ["OpenAIAgentPlannerAdapter"]
