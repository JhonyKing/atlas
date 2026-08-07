"""Deterministic classification and planning before provider-backed graph nodes."""

from __future__ import annotations

import re
from dataclasses import dataclass
from time import perf_counter
from typing import Literal

from atlas.agent.state import AtlasState, Freshness, Intent, NodeEvent, RouteName, RoutePlan


@dataclass(frozen=True, slots=True)
class Classification:
    intent: Intent
    route: RouteName
    language: str
    depth: Literal["short", "deep"]
    risk: Literal["low", "high"]
    freshness: Freshness


def classify_question(request: str, *, language: str | None = None) -> Classification:
    text = request.casefold()
    detected_language = language or (
        "es-MX" if re.search(r"\b(qué|como|cómo|dime|compara)\b", text) else "en-US"
    )
    freshness: Freshness = (
        "temporal"
        if re.search(r"\b(last|latest|recent|year|cambi|últim|año)\b", text)
        else "current"
    )
    if re.search(r"(ignore .*rules|reveal .*key|api key|contraseña|secreto)", text):
        return Classification("unsafe", "abstain", detected_language, "short", "high", freshness)
    if re.search(r"\b(compare|comparison|compara|comparar|versus| vs )\b", text):
        return Classification(
            "comparison", "comparison", detected_language, "deep", "low", freshness
        )
    if re.search(r"\b(report|reporte|document|documento|pdf)\b", text):
        return Classification("report", "report", detected_language, "deep", "low", freshness)
    return Classification("factual", "answer", detected_language, "short", "low", freshness)


def plan_question(request: str, *, classification: Classification | None = None) -> RoutePlan:
    selected = classification or classify_question(request)
    subquestions = [request.strip()]
    if selected.intent == "comparison":
        subquestions = [
            f"{request.strip()} — capabilities",
            f"{request.strip()} — evidence and tradeoffs",
        ]
    return RoutePlan(
        intent=selected.intent,
        route=selected.route,
        subquestions=subquestions,
        source_criteria=["authoritative documentation", "versioned source"],
        date_criteria=["capture date"] if selected.freshness == "temporal" else [],
        freshness=selected.freshness,
        evidence_budget=16 if selected.depth == "deep" else 8,
    )


class AgentOrchestrator:
    """Small deterministic orchestration boundary; provider nodes plug in later."""

    def __init__(self, *, timeout_seconds: float = 15.0) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._timeout_seconds = timeout_seconds

    def prepare(self, state: AtlasState) -> AtlasState:
        classification = classify_question(state.request, language=state.language)
        plan = plan_question(state.request, classification=classification)
        history = [*state.node_history, "classify", "plan"]
        return state.model_copy(
            update={"language": classification.language, "route": plan, "node_history": history}
        )

    def run(self, state: AtlasState, *, cancelled: bool = False) -> AtlasState:
        """Execute deterministic routing nodes; provider work remains behind ports."""

        started = perf_counter()
        prepared = self.prepare(state)
        if perf_counter() - started > self._timeout_seconds:
            return prepared.model_copy(
                update={
                    "node_history": [*prepared.node_history, "abstain"],
                    "errors": ["node_timeout"],
                    "node_events": [
                        NodeEvent(
                            node="abstain",
                            outcome="failed",
                            latency_ms=(perf_counter() - started) * 1000,
                            safe_error="node_timeout",
                        )
                    ],
                }
            )
        if cancelled:
            return prepared.model_copy(
                update={
                    "node_history": [*prepared.node_history, "abstain"],
                    "errors": ["cancelled"],
                    "node_events": [
                        NodeEvent(
                            node="abstain",
                            outcome="cancelled",
                            latency_ms=(perf_counter() - started) * 1000,
                        )
                    ],
                }
            )
        terminal = prepared.route.route
        return prepared.model_copy(
            update={
                "node_history": [*prepared.node_history, terminal],
                "node_events": [
                    NodeEvent(node="classify", outcome="completed", latency_ms=0),
                    NodeEvent(node="plan", outcome="completed", latency_ms=0),
                    NodeEvent(
                        node=terminal,
                        outcome="abstained" if terminal == "abstain" else "completed",
                        latency_ms=(perf_counter() - started) * 1000,
                    ),
                ],
            }
        )
