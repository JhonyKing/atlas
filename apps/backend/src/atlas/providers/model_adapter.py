"""Common provider adapter port; SDK-specific implementations stay elsewhere."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from atlas.models.contracts import ModelRequest


@dataclass(frozen=True, slots=True)
class ModelResponse:
    text: str
    input_tokens: int
    output_tokens: int
    provider_request_id: str | None = None


class ModelAdapter(Protocol):
    provider: str

    async def generate(
        self, request: ModelRequest, *, evidence: Sequence[str]
    ) -> ModelResponse: ...


class DeterministicModelAdapter:
    """Offline adapter used by tests and local development."""

    provider = "demo"

    async def generate(self, request: ModelRequest, *, evidence: Sequence[str]) -> ModelResponse:
        del evidence
        return ModelResponse(
            text=request.prompt,
            input_tokens=len(request.prompt.split()),
            output_tokens=len(request.prompt.split()),
            provider_request_id=None,
        )
