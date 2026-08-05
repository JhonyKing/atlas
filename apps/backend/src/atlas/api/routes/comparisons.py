"""Public HTTP and SSE contract for technology comparisons."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from datetime import UTC, datetime
from typing import Annotated, Literal, Protocol
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, ValidationError

from atlas.comparison.schemas import ComparisonCriterion, ComparisonMatrix, ComparisonRequest
from atlas.domain import CollectionSlug, SourceType
from atlas.observability.context import current_request_id
from atlas.persistence.comparison_quota import ComparisonQuotaExceeded

router = APIRouter(prefix="/v1/comparisons", tags=["Comparisons"])

ComparisonStatusValue = Literal[
    "accepted",
    "retrieving",
    "normalizing",
    "verifying",
    "completed",
    "abstained",
    "cancelled",
    "failed",
]


class ComparisonRunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    status: ComparisonStatusValue
    created_at: datetime
    completed_at: datetime | None = None
    matrix: ComparisonMatrix | None = None
    retained_until: datetime | None = None


class ComparisonRunControl(Protocol):
    async def start(
        self,
        *,
        comparison: Mapping[str, object],
        visitor_key_hash: str,
        idempotency_key: str,
        request_id: UUID,
    ) -> UUID: ...

    async def get_status(
        self,
        run_id: UUID,
        *,
        visitor_key_hash: str,
    ) -> ComparisonRunResponse | None: ...

    async def cancel(self, run_id: UUID, *, visitor_key_hash: str) -> ComparisonRunResponse: ...

    def stream(self, run_id: UUID, *, visitor_key_hash: str) -> AsyncIterator[str]: ...


def _service(request: Request) -> ComparisonRunControl:
    service = request.app.state.comparison_service
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Comparison service is unavailable",
        )
    return service


def _visitor_hash(request: Request) -> str:
    return getattr(request.state, "visitor_key_hash", "development-anonymous-visitor")


def _request_id(request: Request) -> UUID:
    return current_request_id() or UUID(int=0)


def _problem(request: Request, *, status_code: int, detail: str, error_code: str) -> JSONResponse:
    request_id = _request_id(request)
    return JSONResponse(
        status_code=status_code,
        content={
            "type": "about:blank",
            "title": detail,
            "status": status_code,
            "detail": detail,
            "request_id": str(request_id),
            "error_code": error_code,
        },
        media_type="application/problem+json",
        headers={"X-Request-ID": str(request_id)},
    )


@router.post("", response_class=StreamingResponse, response_model=None)
async def create_comparison(
    request: Request,
    raw_body: dict[str, object],
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key",
            min_length=16,
            max_length=128,
            pattern=r"^[A-Za-z0-9._:-]+$",
        ),
    ],
) -> StreamingResponse | JSONResponse:
    try:
        payload = dict(raw_body)
        payload["technologies"] = [CollectionSlug(value) for value in payload["technologies"]]
        payload["criteria"] = [ComparisonCriterion(value) for value in payload["criteria"]]
        if payload.get("product") is not None:
            payload["product"] = CollectionSlug(payload["product"])
        if payload.get("source_type") is not None:
            payload["source_type"] = SourceType(payload["source_type"])
        comparison = ComparisonRequest.model_validate(payload)
    except (ValidationError, ValueError):
        return _problem(
            request,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comparison selection is not valid",
            error_code="invalid_comparison",
        )
    try:
        run_id = await _service(request).start(
            comparison=comparison.model_dump(mode="json"),
            visitor_key_hash=_visitor_hash(request),
            idempotency_key=idempotency_key,
            request_id=_request_id(request),
        )
    except KeyError:
        return _problem(
            request,
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency key conflicts with another comparison",
            error_code="idempotency_conflict",
        )
    except ComparisonQuotaExceeded as exc:
        retry_after = exc.retry_after_seconds(now=datetime.now(UTC))
        return _problem(
            request,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Anonymous comparison quota exceeded",
            error_code="quota_exceeded",
            headers={"Retry-After": str(retry_after)},
        )

    async def stream() -> AsyncIterator[str]:
        async for frame in _service(request).stream(
            run_id, visitor_key_hash=_visitor_hash(request)
        ):
            yield frame

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "X-Atlas-Run-ID": str(run_id),
            "X-Request-ID": str(_request_id(request)),
            "Cache-Control": "no-cache",
        },
    )


@router.get("/{run_id}")
async def get_comparison(request: Request, run_id: UUID) -> JSONResponse:
    value = await _service(request).get_status(run_id, visitor_key_hash=_visitor_hash(request))
    if value is None:
        return _problem(
            request,
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comparison run was not found",
            error_code="not_found",
        )
    response_status = (
        status.HTTP_202_ACCEPTED
        if value.status in {"accepted", "retrieving", "normalizing", "verifying"}
        else status.HTTP_200_OK
    )
    return JSONResponse(
        status_code=response_status,
        content=value.model_dump(mode="json"),
        headers={"X-Request-ID": str(_request_id(request))},
    )


@router.delete("/{run_id}")
async def cancel_comparison(request: Request, run_id: UUID) -> JSONResponse:
    try:
        value = await _service(request).cancel(run_id, visitor_key_hash=_visitor_hash(request))
    except KeyError:
        return _problem(
            request,
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comparison run was not found",
            error_code="not_found",
        )
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=value.model_dump(mode="json"),
        headers={"X-Request-ID": str(_request_id(request))},
    )
