"""Executors that connect comparison retrieval to the explicit workflow."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Protocol
from uuid import UUID

from openai import AsyncOpenAI
from openai.types.shared_params.reasoning import Reasoning

from atlas.comparison.extraction import (
    ComparisonExtraction,
    build_comparison_extraction_input,
    validate_extraction,
)
from atlas.comparison.retrieval import ComparisonRetrievalBranch, ComparisonRetrievalService
from atlas.comparison.schemas import ComparisonMatrix, ComparisonRequest
from atlas.comparison.workflow import ComparisonWorkflow
from atlas.providers.ports import EmbeddingProvider
from atlas.providers.prompts.comparison import COMPARISON_EXTRACTION_INSTRUCTIONS


class ComparisonExtractor(Protocol):
    async def extract(self, branch: ComparisonRetrievalBranch): ...


class OpenAIComparisonObservationExtractor:
    """Use structured output only to extract facts already present in retrieved evidence."""

    def __init__(self, *, client: AsyncOpenAI, model: str, timeout_seconds: float = 20.0) -> None:
        self._client = client
        self._model = model
        self._timeout_seconds = timeout_seconds

    async def extract(self, branch: ComparisonRetrievalBranch):
        response = await asyncio.wait_for(
            self._client.responses.parse(
                model=self._model,
                instructions=COMPARISON_EXTRACTION_INSTRUCTIONS,
                input=build_comparison_extraction_input(branch),
                reasoning=Reasoning(effort="medium", context="current_turn"),
                store=False,
                text_format=ComparisonExtraction,
                tools=[],
            ),
            timeout=self._timeout_seconds,
        )
        extraction = response.output_parsed
        if not isinstance(extraction, ComparisonExtraction):
            raise ValueError("comparison model did not return structured extraction")
        return validate_extraction(
            extraction,
            allowed_evidence_ids=[row.evidence.id for row in branch.rows],
        )


class RetrievalComparisonExecutor:
    """Embed each criterion and run the retrieval/extraction/normalization workflow."""

    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        retrieval: ComparisonRetrievalService,
        extractor: ComparisonExtractor,
        top_k: int = 8,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._workflow = ComparisonWorkflow(retrieval, extractor)
        self._top_k = top_k

    async def run(
        self,
        comparison: ComparisonRequest,
        *,
        snapshot_id: UUID,
        is_cancelled: Callable[[], bool],
    ) -> ComparisonMatrix:
        if is_cancelled():
            raise asyncio.CancelledError
        vectors = await self._embedding_provider.embed(
            [criterion.value.replace("_", " ") for criterion in comparison.criteria]
        )
        if len(vectors) != len(comparison.criteria):
            raise ValueError("embedding provider returned an unexpected vector count")
        embeddings = dict(zip(comparison.criteria, vectors, strict=True))
        return await self._workflow.run(
            comparison,
            snapshot_id=snapshot_id,
            embeddings=embeddings,
            top_k=self._top_k,
            is_cancelled=is_cancelled,
        )
