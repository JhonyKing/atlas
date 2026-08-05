"""Deterministic local services for a provider-free ATLAS development experience."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from uuid import UUID

from pydantic import HttpUrl

from atlas.agent.verification import verify_draft
from atlas.domain import (
    AnswerDraft,
    AnswerStatus,
    Claim,
    ClaimType,
    CollectionSlug,
    CollectionState,
    CollectionStatus,
    CorpusStatus,
    Evidence,
    SourceType,
)
from atlas.providers.ports import AnswerGenerator

_SNAPSHOT_ID = UUID("00000000-0000-0000-0000-000000000801")
_EVIDENCE_IDS = {
    CollectionSlug.LANGGRAPH: UUID("00000000-0000-0000-0000-000000000811"),
    CollectionSlug.LANGCHAIN: UUID("00000000-0000-0000-0000-000000000812"),
    CollectionSlug.OPENAI: UUID("00000000-0000-0000-0000-000000000813"),
}


class DemoCorpusStatusProvider:
    """Return a bounded local baseline, not a production corpus."""

    def get_status(self) -> CorpusStatus:
        now = datetime.now(UTC)
        return CorpusStatus(
            snapshot_id=_SNAPSHOT_ID,
            generated_at=now,
            collections=[
                CollectionStatus(
                    slug=CollectionSlug.LANGGRAPH,
                    name="LangGraph (demo local)",
                    publisher="LangChain",
                    source_types=[SourceType.DOCUMENTATION, SourceType.RELEASE_NOTE],
                    status=CollectionState.UNAVAILABLE,
                    last_success_at=None,
                    last_attempt_at=now,
                    canonical_root=HttpUrl("https://langchain-ai.github.io/langgraph/"),
                ),
                CollectionStatus(
                    slug=CollectionSlug.LANGCHAIN,
                    name="LangChain (demo local)",
                    publisher="LangChain",
                    source_types=[SourceType.DOCUMENTATION, SourceType.CHANGELOG],
                    status=CollectionState.UNAVAILABLE,
                    last_success_at=None,
                    last_attempt_at=now,
                    canonical_root=HttpUrl("https://python.langchain.com/"),
                ),
                CollectionStatus(
                    slug=CollectionSlug.OPENAI,
                    name="OpenAI API (demo local)",
                    publisher="OpenAI",
                    source_types=[SourceType.DOCUMENTATION],
                    status=CollectionState.UNAVAILABLE,
                    last_success_at=None,
                    last_attempt_at=now,
                    canonical_root=HttpUrl("https://platform.openai.com/docs/"),
                ),
            ],
        )


class DemoAnswerGraph:
    """Small deterministic graph substitute for local UI smoke tests.

    It is deliberately not used in production. It returns fixed, inspectable evidence so the
    portfolio journey can be exercised without an OpenAI key or an initialized corpus snapshot.
    """

    async def ainvoke(self, state: Mapping[str, object]) -> dict[str, object]:
        question = state["question"]
        text = getattr(question, "normalized_text", "")
        language = getattr(question, "language", "en-US")
        collection = self._collection_for(text)
        if collection is None:
            limitation = (
                "ATLAS no pudo verificar esta pregunta con el corpus local de demostración."
                if language == "es-MX"
                else "ATLAS could not verify this question with the local demo corpus."
            )
            return {
                "answer": AnswerDraft(
                    answer_status=AnswerStatus.ABSTAINED,
                    limitations=[limitation],
                ),
                "evidence": [],
            }

        evidence = self._evidence(collection)
        claim_text = self._claim_text(collection, language)
        claim = Claim(
            id=UUID("00000000-0000-0000-0000-000000000821"),
            ordinal=0,
            text=claim_text,
            type=ClaimType.FACTUAL,
            citation_ids=[evidence.id],
        )
        return {
            "answer": AnswerDraft(
                answer_status=AnswerStatus.COMPLETE,
                claims=[claim],
                evidence_ids=[evidence.id],
            ),
            "evidence": [evidence],
        }

    @staticmethod
    def _collection_for(text: str) -> CollectionSlug | None:
        if any(
            term in text
            for term in ("langgraph", "conditional edge", "conditional node", "state graph")
        ):
            return CollectionSlug.LANGGRAPH
        if "langchain" in text:
            return CollectionSlug.LANGCHAIN
        if "openai" in text or "responses api" in text:
            return CollectionSlug.OPENAI
        return None

    @staticmethod
    def _evidence(collection: CollectionSlug) -> Evidence:
        data = {
            CollectionSlug.LANGGRAPH: (
                "LangGraph conditional edges route execution to the next node based on the "
                "current graph state.",
                "LangGraph conditional edges",
                "https://langchain-ai.github.io/langgraph/concepts/low_level/",
            ),
            CollectionSlug.LANGCHAIN: (
                "LangChain provides composable building blocks for applications powered by "
                "language models.",
                "LangChain overview",
                "https://python.langchain.com/docs/introduction/",
            ),
            CollectionSlug.OPENAI: (
                "The Responses API is an interface for building model responses with structured "
                "inputs and outputs.",
                "OpenAI Responses API",
                "https://platform.openai.com/docs/api-reference/responses",
            ),
        }[collection]
        return Evidence(
            id=_EVIDENCE_IDS[collection],
            source_title=data[1],
            publisher="LangChain" if collection is not CollectionSlug.OPENAI else "OpenAI",
            canonical_url=HttpUrl(data[2]),
            excerpt=data[0],
            captured_at=datetime(2026, 8, 5, tzinfo=UTC),
            source_type=SourceType.DOCUMENTATION,
        )

    @staticmethod
    def _claim_text(collection: CollectionSlug, language: str) -> str:
        if language == "es-MX":
            return {
                CollectionSlug.LANGGRAPH: (
                    "En LangGraph, las aristas condicionales dirigen la ejecución al siguiente "
                    "nodo según el estado actual del grafo."
                ),
                CollectionSlug.LANGCHAIN: (
                    "LangChain ofrece bloques componibles para aplicaciones impulsadas por "
                    "modelos de lenguaje."
                ),
                CollectionSlug.OPENAI: (
                    "La Responses API de OpenAI permite construir respuestas de modelos con "
                    "entradas y salidas estructuradas."
                ),
            }[collection]
        return {
            CollectionSlug.LANGGRAPH: (
                "In LangGraph, conditional edges route execution to the next node based on the "
                "current graph state."
            ),
            CollectionSlug.LANGCHAIN: (
                "LangChain provides composable building blocks for applications powered by "
                "language models."
            ),
            CollectionSlug.OPENAI: (
                "The OpenAI Responses API supports model responses with structured inputs and "
                "outputs."
            ),
        }[collection]


class OpenAIConnectedDemoGraph:
    """Use the configured OpenAI generator with the same bounded local evidence pack.

    This is a development bridge, not the production retrieval graph. It proves the provider
    connection and citation gate through the browser while the real corpus snapshot is still being
    populated.
    """

    def __init__(self, generator: AnswerGenerator) -> None:
        self._generator = generator

    async def ainvoke(self, state: Mapping[str, object]) -> dict[str, object]:
        question = state["question"]
        text = getattr(question, "normalized_text", "")
        collection = DemoAnswerGraph._collection_for(text)
        language = getattr(question, "language", "en-US")
        if collection is None:
            limitation = (
                "ATLAS no pudo verificar esta pregunta con el corpus local de demostración."
                if language == "es-MX"
                else "ATLAS could not verify this question with the local demo corpus."
            )
            return {
                "answer": AnswerDraft(
                    answer_status=AnswerStatus.ABSTAINED,
                    limitations=[limitation],
                ),
                "evidence": [],
            }

        evidence = DemoAnswerGraph._evidence(collection)
        try:
            draft = await self._generator.generate(
                question,
                [evidence],
                request_id=state.get("request_id"),
            )
        except Exception:
            limitation = (
                "El proveedor de modelo no respondió; ATLAS no publicará una respuesta sin "
                "verificar."
                if language == "es-MX"
                else (
                    "The model provider did not respond; ATLAS will not publish an unverified "
                    "answer."
                )
            )
            return {
                "answer": AnswerDraft(
                    answer_status=AnswerStatus.ABSTAINED,
                    limitations=[limitation],
                ),
                "evidence": [],
            }

        verification = verify_draft(
            draft,
            [evidence],
            question=question,
            request_id=state.get("request_id"),
        )
        if verification.error is not None or verification.draft is None:
            limitation = (
                "La respuesta del modelo no superó la verificación de citas."
                if language == "es-MX"
                else "The model response did not pass citation verification."
            )
            return {
                "answer": AnswerDraft(
                    answer_status=AnswerStatus.ABSTAINED,
                    limitations=[limitation],
                ),
                "evidence": [],
            }
        return {"answer": verification.draft, "evidence": [evidence]}


__all__ = ["DemoAnswerGraph", "DemoCorpusStatusProvider", "OpenAIConnectedDemoGraph"]
