"""Small, explicit LangGraph for verified cited answers."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal, NotRequired, Protocol, TypedDict, cast
from uuid import UUID, uuid4

from langgraph.graph import END, START, StateGraph

from atlas.agent.verification import verify_draft
from atlas.domain import (
    AnswerDraft,
    AnswerStatus,
    CollectionSlug,
    ControlledError,
    ErrorCode,
    Evidence,
    Question,
)
from atlas.providers.ports import AnswerGenerator, EmbeddingProvider, ProviderRefusal
from atlas.retrieval.service import RetrievalRow

GraphStage = Literal[
    "accepted",
    "validated",
    "retrieving",
    "evidence_gate",
    "composing",
    "verifying",
    "finalized",
    "abstained",
]


class EvidenceRetriever(Protocol):
    async def retrieve(
        self,
        question: Question,
        embedding: list[float],
        *,
        top_k: int = 8,
    ) -> Sequence[RetrievalRow]: ...


class CitedAnswerState(TypedDict):
    question: Question
    request_id: NotRequired[UUID]
    cancelled: NotRequired[bool]
    stage: NotRequired[GraphStage]
    visited: NotRequired[list[str]]
    evidence: NotRequired[list[Evidence]]
    draft: NotRequired[AnswerDraft | None]
    answer: NotRequired[AnswerDraft | None]
    error: NotRequired[ControlledError | None]


@dataclass(frozen=True, slots=True)
class CitedAnswerDependencies:
    embedding_provider: EmbeddingProvider
    retriever: EvidenceRetriever
    answer_generator: AnswerGenerator
    top_k: int = 8
    timeout_seconds: float = 15.0

    def __post_init__(self) -> None:
        if not 1 <= self.top_k <= 50:
            raise ValueError("top_k must be between 1 and 50")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


class CitedAnswerGraph:
    """Compile and execute the graph with dependencies isolated per graph instance."""

    def __init__(self, dependencies: CitedAnswerDependencies) -> None:
        self._dependencies = dependencies
        self._compiled = self._build().compile()

    async def ainvoke(self, state: Mapping[str, object]) -> CitedAnswerState:
        input_state = cast(CitedAnswerState, dict(state))
        result = await self._compiled.ainvoke(input_state)
        return cast(CitedAnswerState, result)

    def _build(self) -> StateGraph[CitedAnswerState]:
        builder = StateGraph(CitedAnswerState)
        builder.add_node("validate", self._validate)
        builder.add_node("retrieve", self._retrieve)
        builder.add_node("evidence_gate", self._evidence_gate)
        builder.add_node("compose", self._compose)
        builder.add_node("verify", self._verify)
        builder.add_node("abstain", self._abstain)
        builder.add_node("finalize", self._finalize)
        builder.add_edge(START, "validate")
        builder.add_conditional_edges(
            "validate",
            self._route_after_validate,
            {"retrieve": "retrieve", "abstain": "abstain"},
        )
        builder.add_conditional_edges(
            "retrieve",
            self._route_after_retrieve,
            {"evidence_gate": "evidence_gate", "abstain": "abstain"},
        )
        builder.add_conditional_edges(
            "evidence_gate",
            self._route_after_evidence,
            {"compose": "compose", "abstain": "abstain"},
        )
        builder.add_conditional_edges(
            "compose",
            self._route_after_compose,
            {"verify": "verify", "abstain": "abstain"},
        )
        builder.add_conditional_edges(
            "verify",
            self._route_after_verify,
            {"finalize": "finalize", "abstain": "abstain"},
        )
        builder.add_edge("abstain", END)
        builder.add_edge("finalize", END)
        return builder

    async def _validate(self, state: CitedAnswerState) -> dict[str, object]:
        visited = _visit(state, "validate")
        if state.get("cancelled", False):
            return {
                "visited": visited,
                "stage": "abstained",
                "error": _controlled_error(
                    state,
                    ErrorCode.CANCELLED,
                    "The answer request was cancelled before retrieval.",
                ),
            }
        return {"visited": visited, "stage": "validated"}

    async def _retrieve(self, state: CitedAnswerState) -> dict[str, object]:
        visited = _visit(state, "retrieve")
        question = state["question"]
        try:
            vectors = await self._dependencies.embedding_provider.embed(
                [_retrieval_query(question.normalized_text)]
            )
            if len(vectors) != 1:
                raise ValueError("embedding provider returned an unexpected vector count")
            retrieval_question = _scoped_question(question)
            rows = await self._dependencies.retriever.retrieve(
                retrieval_question,
                vectors[0],
                top_k=self._dependencies.top_k,
            )
            return {
                "visited": visited,
                "stage": "retrieving",
                "evidence": [row.evidence for row in rows],
            }
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            return {
                "visited": visited,
                "stage": "abstained",
                "error": _controlled_error(
                    state,
                    ErrorCode.CORPUS_UNAVAILABLE,
                    "The evidence corpus could not be queried.",
                ),
                "error_detail": str(exc),
            }

    async def _evidence_gate(self, state: CitedAnswerState) -> dict[str, object]:
        visited = _visit(state, "evidence_gate")
        if not state.get("evidence"):
            return {
                "visited": visited,
                "stage": "abstained",
                "error": _controlled_error(
                    state,
                    ErrorCode.INSUFFICIENT_EVIDENCE,
                    "No retrieved evidence supports this question.",
                ),
            }
        return {"visited": visited, "stage": "evidence_gate"}

    async def _compose(self, state: CitedAnswerState) -> dict[str, object]:
        visited = _visit(state, "compose")
        try:
            draft = await asyncio.wait_for(
                self._dependencies.answer_generator.generate(
                    state["question"],
                    state.get("evidence", []),
                    request_id=state.get("request_id"),
                ),
                timeout=self._dependencies.timeout_seconds,
            )
            return {"visited": visited, "stage": "composing", "draft": draft}
        except asyncio.CancelledError:
            raise
        except TimeoutError:
            return {
                "visited": visited,
                "stage": "abstained",
                "error": _controlled_error(
                    state,
                    ErrorCode.PROVIDER_UNAVAILABLE,
                    "The answer provider timed out before producing a verified draft.",
                ),
            }
        except ProviderRefusal:
            return {
                "visited": visited,
                "stage": "abstained",
                "error": _controlled_error(
                    state,
                    ErrorCode.UNSUPPORTED_QUESTION,
                    "The provider declined because this question is outside the supported corpus.",
                ),
            }
        except Exception:
            return {
                "visited": visited,
                "stage": "abstained",
                "error": _controlled_error(
                    state,
                    ErrorCode.PROVIDER_UNAVAILABLE,
                    "The answer provider could not produce a structured draft.",
                ),
            }

    async def _verify(self, state: CitedAnswerState) -> dict[str, object]:
        visited = _visit(state, "verify")
        draft = state.get("draft")
        if draft is None:
            return {
                "visited": visited,
                "stage": "abstained",
                "error": _controlled_error(
                    state,
                    ErrorCode.CITATION_VERIFICATION_FAILED,
                    "The provider returned no structured draft.",
                ),
            }
        verification = verify_draft(
            draft,
            state.get("evidence", []),
            question=state["question"],
            request_id=state.get("request_id"),
        )
        if verification.error is not None:
            return {
                "visited": visited,
                "stage": "abstained",
                "error": verification.error,
            }
        return {"visited": visited, "stage": "verifying", "draft": verification.draft}

    async def _abstain(self, state: CitedAnswerState) -> dict[str, object]:
        visited = _visit(state, "abstain")
        error = state.get("error")
        limitation = (
            error.message
            if error is not None
            else "ATLAS could not verify a supported answer from the available evidence."
        )
        answer = AnswerDraft(answer_status=AnswerStatus.ABSTAINED, limitations=[limitation])
        return {"visited": visited, "stage": "abstained", "answer": answer}

    async def _finalize(self, state: CitedAnswerState) -> dict[str, object]:
        visited = _visit(state, "finalize")
        draft = state.get("draft")
        if draft is None:
            return {"visited": visited, "stage": "abstained"}
        return {"visited": visited, "stage": "finalized", "answer": draft}

    @staticmethod
    def _route_after_validate(state: CitedAnswerState) -> str:
        return "abstain" if state.get("error") is not None else "retrieve"

    @staticmethod
    def _route_after_retrieve(state: CitedAnswerState) -> str:
        return "abstain" if state.get("error") is not None else "evidence_gate"

    @staticmethod
    def _route_after_evidence(state: CitedAnswerState) -> str:
        return "abstain" if state.get("error") is not None else "compose"

    @staticmethod
    def _route_after_compose(state: CitedAnswerState) -> str:
        return "abstain" if state.get("error") is not None else "verify"

    @staticmethod
    def _route_after_verify(state: CitedAnswerState) -> str:
        return "abstain" if state.get("error") is not None else "finalize"


def _visit(state: CitedAnswerState, node: str) -> list[str]:
    return [*state.get("visited", []), node]


_TEMPORAL_QUERY_RE = re.compile(
    r"\b(last|past|previous|recent|latest|changed|change|new|release|year|quarter)\b"
    r"|\b(últim[oa]s?|cambi[óo]|nuev[oa]s?|lanzamientos?|año)\b",
    re.IGNORECASE,
)


def _retrieval_query(normalized_question: str) -> str:
    """Add bounded temporal vocabulary so change questions reach release/version chunks."""

    if not _TEMPORAL_QUERY_RE.search(normalized_question):
        return normalized_question
    return f"{normalized_question} releases changes new models version history dated 2025 2026"


def _scoped_question(question: Question) -> Question:
    """Narrow retrieval when the visitor names one supported product explicitly."""

    if question.product is not None:
        return question
    text = question.normalized_text
    terms = (
        (CollectionSlug.LANGGRAPH, ("langgraph",)),
        (CollectionSlug.LANGCHAIN, ("langchain",)),
        (CollectionSlug.OPENAI, ("openai", "responses api")),
        (CollectionSlug.ANTHROPIC, ("anthropic", "claude")),
        (CollectionSlug.GEMINI, ("gemini",)),
    )
    for collection, candidates in terms:
        if any(candidate in text for candidate in candidates):
            return question.model_copy(update={"product": collection})
    return question


def _controlled_error(
    state: CitedAnswerState,
    code: ErrorCode,
    message: str,
) -> ControlledError:
    return ControlledError(
        code=code,
        message=message,
        retryable=code is ErrorCode.PROVIDER_UNAVAILABLE,
        request_id=state.get("request_id", uuid4()),
    )
