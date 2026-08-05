"""Retained answer feedback contract."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import suppress
from typing import Annotated, Literal, Protocol
from uuid import UUID, uuid4

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field

from atlas.observability.context import current_request_id
from atlas.persistence.review_cases import ReviewCategory

router = APIRouter(prefix="/v1/answers", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: Literal["useful", "not_useful"]
    category: Literal[
        "incorrect_citation",
        "incorrect_answer",
        "outdated",
        "incomplete",
        "other",
    ] | None = None
    comment: Annotated[str, Field(max_length=1000)] | None = None


class FeedbackNotFound(RuntimeError):
    """The answer does not exist for the current visitor."""


class FeedbackExpired(RuntimeError):
    """The answer content has crossed its retention boundary."""


class FeedbackServiceUnavailable(RuntimeError):
    """No feedback persistence implementation is configured."""


class FeedbackControl(Protocol):
    async def put(
        self,
        run_id: UUID,
        *,
        visitor_key_hash: str,
        feedback: Mapping[str, object],
    ) -> None: ...


class ReviewCaseControl(Protocol):
    async def enqueue(
        self,
        answer_run_id: UUID,
        *,
        category: ReviewCategory,
        label: Literal["useful", "not_useful"],
    ) -> object: ...


def _service(request: Request) -> FeedbackControl:
    service = request.app.state.feedback_service
    if service is None:
        raise FeedbackServiceUnavailable
    return service


def _visitor_hash(request: Request) -> str:
    return getattr(request.state, "visitor_key_hash", "development-anonymous-visitor")


def _problem(request: Request, *, status_code: int, detail: str, error_code: str) -> JSONResponse:
    request_id = str(current_request_id() or uuid4())
    payload = {
        "type": "about:blank",
        "title": detail,
        "status": status_code,
        "detail": detail,
        "request_id": request_id,
        "error_code": error_code,
    }
    return JSONResponse(
        status_code=status_code,
        content=payload,
        media_type="application/problem+json",
        headers={"X-Request-ID": request_id},
    )


@router.put("/{run_id}/feedback", status_code=status.HTTP_204_NO_CONTENT)
async def put_feedback(request: Request, run_id: UUID, body: FeedbackRequest) -> Response:
    try:
        service = _service(request)
        await service.put(
            run_id,
            visitor_key_hash=_visitor_hash(request),
            feedback=body.model_dump(mode="json"),
        )
        review_service: ReviewCaseControl | None = request.app.state.review_case_service
        if body.category == "incorrect_citation" and review_service is not None:
            with suppress(Exception):
                await review_service.enqueue(
                    run_id,
                    category=body.category,
                    label=body.label,
                )
    except FeedbackNotFound:
        return _problem(
            request,
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer run was not found",
            error_code="not_found",
        )
    except FeedbackExpired:
        return _problem(
            request,
            status_code=status.HTTP_410_GONE,
            detail="Answer content and feedback window have expired",
            error_code="retention_expired",
        )
    except FeedbackServiceUnavailable:
        return _problem(
            request,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Feedback service is unavailable",
            error_code="feedback_unavailable",
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"X-Request-ID": str(current_request_id() or uuid4())},
    )
