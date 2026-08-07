"""Typed, content-safe state contracts for the explicit agent workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

Intent = Literal["factual", "comparison", "report", "unsafe", "unsupported"]
RouteName = Literal["answer", "comparison", "report", "abstain"]
Freshness = Literal["current", "temporal", "any"]


class RoutePlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: Intent = "factual"
    route: RouteName = "answer"
    subquestions: list[str] = Field(default_factory=list, max_length=8)
    source_criteria: list[str] = Field(default_factory=list, max_length=8)
    date_criteria: list[str] = Field(default_factory=list, max_length=4)
    freshness: Freshness = "current"
    evidence_budget: int = Field(default=8, ge=1, le=32)


class NodeEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node: str
    outcome: Literal["completed", "abstained", "cancelled", "failed"]
    latency_ms: float = Field(ge=0)
    safe_error: str | None = None


class AtlasState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    thread_id: UUID = Field(default_factory=uuid4)
    request_id: UUID = Field(default_factory=uuid4)
    user_id: UUID | None = None
    request: str = Field(min_length=1, max_length=4000)
    language: str = "en-US"
    route: RoutePlan = Field(default_factory=RoutePlan)
    evidence_ids: list[str] = Field(default_factory=list, max_length=64)
    citations: list[str] = Field(default_factory=list, max_length=64)
    answer_id: UUID | None = None
    report_id: UUID | None = None
    quality: str | None = None
    errors: list[str] = Field(default_factory=list, max_length=8)
    node_history: list[str] = Field(default_factory=list, max_length=64)
    node_events: list[NodeEvent] = Field(default_factory=list, max_length=64)
    state_version: int = Field(default=1, ge=1)
    corpus_version: str = "unknown"
    prompt_version: str = "unknown"
    model_version: str = "unknown"
    checkpoint_id: UUID | None = None
    review_status: Literal["not_required", "pending", "approved", "edited", "rejected"] = (
        "not_required"
    )
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
