"""OpenAI Responses adapter kept behind the ATLAS AnswerGenerator port."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal
from uuid import UUID

from openai import APIConnectionError, APIStatusError, AsyncOpenAI
from openai.types.shared_params.reasoning import Reasoning

from atlas.domain import AnswerDraft, Evidence, Question
from atlas.providers.prompts.cited_answer import (
    CITED_ANSWER_INSTRUCTIONS,
    CITED_ANSWER_TOOLS,
    build_cited_answer_input,
)

MODEL_ID = "gpt-5.6-luna"
REASONING_EFFORT: Literal["medium"] = "medium"
_RETRYABLE_STATUS_CODES = frozenset({408, 409, 429, 500, 502, 503, 504})
_SAFETY_IDENTIFIER_RE = re.compile(r"^[0-9a-f]{64}$")


class ProviderAdapterError(RuntimeError):
    """Safe adapter error; provider response bodies are deliberately not exposed."""

    def __init__(self, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable


@dataclass(frozen=True, slots=True)
class ResponseTelemetry:
    response_id: str | None
    request_id: str | None
    model: str | None
    input_tokens: int | None
    output_tokens: int | None
    reasoning_tokens: int | None
    cached_tokens: int | None


def derive_safety_identifier(secret: str, visitor_key: str) -> str:
    """Derive a stable, non-reversible provider safety identifier from a visitor key."""

    if not secret:
        raise ValueError("safety identifier secret must not be empty")
    return hmac.new(
        secret.encode("utf-8"),
        visitor_key.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


class OpenAIResponsesAdapter:
    """Structured Responses API adapter with bounded, safe retries."""

    def __init__(
        self,
        *,
        client: AsyncOpenAI,
        safety_identifier: str,
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
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self.last_telemetry: ResponseTelemetry | None = None

    async def generate(
        self,
        question: Question,
        evidence: Sequence[Evidence],
        *,
        request_id: UUID | None = None,
    ) -> AnswerDraft:
        del request_id
        input_text = self._build_input(question, evidence)

        for attempt in range(self._max_retries + 1):
            try:
                reasoning: Reasoning = {"effort": REASONING_EFFORT, "context": "current_turn"}
                response = await self._client.responses.parse(
                    model=MODEL_ID,
                    instructions=CITED_ANSWER_INSTRUCTIONS,
                    input=input_text,
                    reasoning=reasoning,
                    safety_identifier=self._safety_identifier,
                    store=False,
                    text_format=AnswerDraft,
                    tools=list(CITED_ANSWER_TOOLS),
                )
            except (APIConnectionError, APIStatusError) as exc:
                retryable = self._is_retryable(exc)
                if retryable and attempt < self._max_retries:
                    if self._retry_delay:
                        await asyncio.sleep(self._retry_delay * (2**attempt))
                    continue
                raise ProviderAdapterError(
                    "provider request failed",
                    retryable=retryable,
                ) from exc
            except Exception as exc:
                if attempt < self._max_retries:
                    if self._retry_delay:
                        await asyncio.sleep(self._retry_delay * (2**attempt))
                    continue
                raise ProviderAdapterError("provider response could not be parsed") from exc

            parsed = response.output_parsed
            if not isinstance(parsed, AnswerDraft):
                raise ProviderAdapterError("provider response did not contain a structured draft")
            self.last_telemetry = self._telemetry(response)
            return parsed

        raise AssertionError("retry loop must return or raise")

    @staticmethod
    def _build_input(question: Question, evidence: Sequence[Evidence]) -> str:
        return build_cited_answer_input(question, evidence)

    @staticmethod
    def _is_retryable(error: APIConnectionError | APIStatusError) -> bool:
        if isinstance(error, APIConnectionError):
            return True
        return error.status_code in _RETRYABLE_STATUS_CODES

    @staticmethod
    def _telemetry(response: Any) -> ResponseTelemetry:
        usage = getattr(response, "usage", None)
        input_details = getattr(usage, "input_tokens_details", None)
        output_details = getattr(usage, "output_tokens_details", None)
        return ResponseTelemetry(
            response_id=getattr(response, "id", None),
            request_id=getattr(response, "_request_id", None),
            model=getattr(response, "model", None),
            input_tokens=getattr(usage, "input_tokens", None),
            output_tokens=getattr(usage, "output_tokens", None),
            reasoning_tokens=getattr(output_details, "reasoning_tokens", None),
            cached_tokens=getattr(input_details, "cached_tokens", None),
        )
