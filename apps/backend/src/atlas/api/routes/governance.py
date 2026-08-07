"""Operator-facing curated corpus governance status."""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from atlas.ingestion.governance import GovernanceError, InMemoryGovernanceRepository

router = APIRouter(prefix="/v1/corpus/governance", tags=["Corpus governance"])


class GovernedCollectionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    display_name: str
    kind: str
    policy_state: str
    enabled: bool
    source_count: int = Field(ge=0)
    stale_count: int = Field(ge=0)
    disabled_count: int = Field(ge=0)
    retry_count: int = Field(ge=0)
    dead_letter_count: int = Field(ge=0)


class GovernanceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    collections: list[GovernedCollectionResponse]
    coverage: dict[str, object]


def _service(request: Request) -> InMemoryGovernanceRepository | None:
    return cast(InMemoryGovernanceRepository | None, request.app.state.governance_service)


@router.get("", response_model=GovernanceResponse)
def get_governance(request: Request) -> GovernanceResponse | JSONResponse:
    service = _service(request)
    if service is None:
        return JSONResponse(status_code=503, content={"detail": "Governance unavailable"})
    coverage = service.coverage()
    rows = [GovernedCollectionResponse.model_validate(row) for row in coverage.collections]
    return GovernanceResponse(
        collections=rows,
        coverage={
            "captured_at": coverage.captured_at.isoformat(),
            "collection_count": coverage.collection_count,
            "dead_letter_count": coverage.dead_letter_count,
            "window_days": coverage.window_days,
            "target_met": coverage.target_met,
        },
    )


@router.post("/{collection}/disable", status_code=status.HTTP_202_ACCEPTED)
def disable_collection(collection: str, request: Request) -> JSONResponse:
    service = _service(request)
    if service is None:
        return JSONResponse(status_code=503, content={"detail": "Governance unavailable"})
    try:
        service.disable_collection(collection, reason="operator request")
    except GovernanceError:
        return JSONResponse(status_code=404, content={"detail": "Collection not found"})
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"status": "disabled"})
