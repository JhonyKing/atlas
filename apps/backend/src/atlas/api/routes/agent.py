"""Safe API boundary for deterministic planning and human review decisions."""

from __future__ import annotations

from typing import Literal, cast
from uuid import UUID

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

from atlas.agent.orchestration import AgentOrchestrator
from atlas.agent.review import ReviewService
from atlas.agent.state import AtlasState

router = APIRouter(prefix="/v1/agent", tags=["Agent orchestration"])


class PrepareRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request: str = Field(min_length=1, max_length=4000)
    language: str = "en-US"
    thread_id: UUID | None = None


class ReviewCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: UUID
    evidence_ids: list[str] = Field(min_length=1, max_length=64)
    proposed_text: str = Field(min_length=1, max_length=20_000)
    reviewer_id: str = Field(min_length=1, max_length=128)


class ReviewDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reviewer_id: str = Field(min_length=1, max_length=128)
    action: Literal["approve", "edit", "reject"]
    decision_key: str = Field(min_length=1, max_length=128)
    edited_text: str | None = Field(default=None, max_length=20_000)


def _review(request: Request) -> ReviewService:
    return cast(ReviewService, request.app.state.agent_review_service)


@router.post("/prepare")
def prepare(payload: PrepareRequest, request: Request) -> dict[str, object]:
    orchestrator = cast(AgentOrchestrator, request.app.state.agent_orchestrator)
    if payload.thread_id is None:
        state = orchestrator.run(AtlasState(request=payload.request, language=payload.language))
    else:
        state = orchestrator.run(
            AtlasState(
                request=payload.request,
                language=payload.language,
                thread_id=payload.thread_id,
            )
        )
    return {
        "thread_id": str(state.thread_id),
        "route": state.route.model_dump(mode="json"),
        "node_history": state.node_history,
        "errors": state.errors,
    }


@router.post("/reviews")
def create_review(payload: ReviewCreateRequest, request: Request) -> dict[str, object]:
    review = _review(request).create(**payload.model_dump())
    return {
        "id": str(review.id),
        "status": review.status.value,
        "expires_at": review.expires_at.isoformat(),
    }


@router.post("/reviews/{review_id}/decision")
def decide_review(
    review_id: UUID, payload: ReviewDecisionRequest, request: Request
) -> dict[str, object]:
    review = _review(request).decide(review_id, **payload.model_dump())
    return {
        "id": str(review.id),
        "status": review.status.value,
        "decision_key": review.decision_key,
    }
