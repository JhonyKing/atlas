"""OpenAI embeddings adapter with a versioned dimension invariant."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from openai import AsyncOpenAI

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


@dataclass(frozen=True, slots=True)
class EmbeddingProfile:
    provider: str
    model: str
    dimensions: int
    distance_metric: str
    normalization_version: str


DEFAULT_EMBEDDING_PROFILE = EmbeddingProfile(
    provider="openai",
    model=EMBEDDING_MODEL,
    dimensions=EMBEDDING_DIMENSIONS,
    distance_metric="cosine",
    normalization_version="atlas-embedding-v1",
)


class EmbeddingAdapterError(RuntimeError):
    """Safe error for malformed or unavailable embedding responses."""


class OpenAIEmbeddingsAdapter:
    dimensions = DEFAULT_EMBEDDING_PROFILE.dimensions

    def __init__(
        self,
        *,
        client: AsyncOpenAI,
        profile: EmbeddingProfile = DEFAULT_EMBEDDING_PROFILE,
    ) -> None:
        if profile.model != EMBEDDING_MODEL or profile.dimensions != EMBEDDING_DIMENSIONS:
            raise ValueError("the adapter requires the launch embedding profile")
        self._client = client
        self.profile = profile

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            raise ValueError("embedding input must contain at least one text")
        if any(not isinstance(text, str) or not text for text in texts):
            raise ValueError("embedding input texts must be non-empty strings")

        try:
            response = await self._client.embeddings.create(
                model=self.profile.model,
                input=list(texts),
                dimensions=self.profile.dimensions,
                encoding_format="float",
            )
        except Exception as exc:
            raise EmbeddingAdapterError("embedding provider request failed") from exc

        if len(response.data) != len(texts):
            raise EmbeddingAdapterError("embedding response item count does not match input")

        vectors: list[list[float] | None] = [None] * len(texts)
        for item in response.data:
            index = item.index
            if index < 0 or index >= len(texts) or vectors[index] is not None:
                raise EmbeddingAdapterError("embedding response index is invalid")
            vector = list(item.embedding)
            if len(vector) != self.profile.dimensions:
                raise EmbeddingAdapterError("embedding vector dimension mismatch")
            if not all(math.isfinite(value) for value in vector):
                raise EmbeddingAdapterError("embedding vector contains a non-finite value")
            vectors[index] = vector

        if any(vector is None for vector in vectors):
            raise EmbeddingAdapterError("embedding response is missing an index")
        return [vector for vector in vectors if vector is not None]
