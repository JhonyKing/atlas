"""Provider-independent ports and value objects for ATLAS integrations."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol, runtime_checkable
from uuid import UUID

from atlas.domain import AnswerDraft, Evidence, Question


class ProviderRefusal(RuntimeError):
    """The provider declined a question because it is outside supported scope."""


@dataclass(frozen=True, slots=True)
class FetchedSource:
    requested_url: str
    final_url: str
    content: bytes
    content_type: str
    fetched_at: datetime
    etag: str | None = None
    last_modified: str | None = None


@dataclass(frozen=True, slots=True)
class ModelPrice:
    model_id: str
    effective_from: datetime
    input_per_million: Decimal
    output_per_million: Decimal
    reasoning_per_million: Decimal | None = None
    cache_read_per_million: Decimal | None = None
    cache_write_per_million: Decimal | None = None


@runtime_checkable
class AnswerGenerator(Protocol):
    async def generate(
        self,
        question: Question,
        evidence: Sequence[Evidence],
        *,
        request_id: UUID | None = None,
    ) -> AnswerDraft: ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    dimensions: int

    async def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


@runtime_checkable
class Clock(Protocol):
    def now(self) -> datetime: ...


@runtime_checkable
class PriceTable(Protocol):
    def get(self, model_id: str, observed_at: datetime) -> ModelPrice | None: ...


@runtime_checkable
class SourceFetcher(Protocol):
    async def fetch(self, url: str) -> FetchedSource: ...
