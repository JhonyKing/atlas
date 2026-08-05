"""Operator-only view of PII-minimized feedback review cases."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, ConfigDict

from atlas.api.routes.operator_ingestion import require_operator
from atlas.persistence.review_cases import ReviewCaseListing, ReviewCaseRecord

router = APIRouter(prefix="/v1/operator", tags=["Review"])


class ReviewCaseResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    answer_run_id: UUID
    category: str
    label: str
    created_at: datetime


def _service(request: Request) -> ReviewCaseListing:
    service = request.app.state.review_case_service
    if service is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Review-case service is unavailable",
        )
    return service


def _response(record: ReviewCaseRecord) -> ReviewCaseResponse:
    return ReviewCaseResponse(
        id=record.id,
        answer_run_id=record.answer_run_id,
        category=record.category,
        label=record.label,
        created_at=record.created_at,
    )


@router.get("/review-cases", response_model=list[ReviewCaseResponse])
def list_review_cases(
    request: Request,
    _token: Annotated[str, Depends(require_operator)],
) -> list[ReviewCaseResponse]:
    return [_response(record) for record in _service(request).list_cases()]
