"""Deterministic provider fakes for unit and offline-evaluation tests."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from uuid import NAMESPACE_URL, UUID, uuid5

from atlas.domain import AnswerDraft, AnswerStatus, Claim, ClaimType, Evidence, Question
from atlas.providers.ports import FetchedSource, ModelPrice


class DeterministicAnswerGenerator:
    def __init__(self) -> None:
        self.calls = 0

    async def generate(
        self,
        question: Question,
        evidence: Sequence[Evidence],
        *,
        request_id: UUID | None = None,
    ) -> AnswerDraft:
        del question, request_id
        self.calls += 1
        if not evidence:
            return AnswerDraft(
                answer_status=AnswerStatus.ABSTAINED,
                limitations=["No evidence was available in the deterministic fixture."],
            )

        first_evidence = evidence[0]
        citation_id = uuid5(NAMESPACE_URL, f"atlas-fake-citation:{first_evidence.id}")
        return AnswerDraft(
            answer_status=AnswerStatus.COMPLETE,
            claims=[
                Claim(
                    id=uuid5(NAMESPACE_URL, f"atlas-fake-claim:{first_evidence.id}"),
                    ordinal=0,
                    text="The fixture contains supporting official evidence.",
                    type=ClaimType.FACTUAL,
                    citation_ids=[citation_id],
                )
            ],
            evidence_ids=[first_evidence.id],
        )


class DeterministicEmbeddingProvider:
    def __init__(self, dimensions: int = 1536) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            vectors.append(
                [
                    (digest[index % len(digest)] / 255.0) * 2.0 - 1.0
                    for index in range(self.dimensions)
                ]
            )
        return vectors


@dataclass(frozen=True, slots=True)
class FixedClock:
    current: datetime

    def now(self) -> datetime:
        return self.current


class StaticPriceTable:
    def __init__(self, prices: Sequence[ModelPrice]) -> None:
        self._prices = tuple(prices)

    def get(self, model_id: str, observed_at: datetime) -> ModelPrice | None:
        candidates = [
            price
            for price in self._prices
            if price.model_id == model_id and price.effective_from <= observed_at
        ]
        return max(candidates, key=lambda price: price.effective_from) if candidates else None


class FixtureSourceFetcher:
    def __init__(self, fixtures: dict[str, FetchedSource]) -> None:
        self._fixtures = dict(fixtures)

    async def fetch(self, url: str) -> FetchedSource:
        try:
            return self._fixtures[url]
        except KeyError as exc:
            raise LookupError(f"no source fixture for {url}") from exc
