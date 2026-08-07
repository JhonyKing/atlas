"""Authenticated operator controls for durable corpus refreshes."""

from __future__ import annotations

import hmac
from datetime import datetime
from typing import Annotated, Literal, cast
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field

from atlas.domain import CollectionSlug
from atlas.ingestion.service import IdempotencyConflict, OperatorIngestionService
from atlas.observability.context import current_request_id

router = APIRouter(prefix="/v1/operator", tags=["Operator"])
bearer = HTTPBearer(auto_error=False)


class EnqueueIngestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    collection: CollectionSlug


class IngestionRunStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    collection: CollectionSlug
    trigger: Literal["scheduled", "operator"]
    status: Literal["queued", "running", "succeeded", "partial", "failed", "dead_letter"]
    requested_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    attempt_count: Annotated[int, Field(ge=0)] = 0
    discovered_count: Annotated[int, Field(ge=0)] = 0
    promoted_count: Annotated[int, Field(ge=0)] = 0
    failed_count: Annotated[int, Field(ge=0)] = 0
    error_code: str | None = None


def require_operator(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> str:
    expected = request.app.state.operator_token
    if (
        credentials is None
        or not expected
        or not hmac.compare_digest(credentials.credentials, expected)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return credentials.credentials


def _service(request: Request) -> OperatorIngestionService:
    service = request.app.state.operator_service
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Operator ingestion is unavailable",
        )
    return cast(OperatorIngestionService, service)


def _response(payload: IngestionRunStatus, *, status_code: int) -> JSONResponse:
    response = JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))
    response.headers["X-Request-ID"] = str(current_request_id() or uuid4())
    return response


@router.post(
    "/ingestion-runs",
    response_model=IngestionRunStatus,
    status_code=status.HTTP_202_ACCEPTED,
)
def enqueue_ingestion_run(
    request: Request,
    body: EnqueueIngestionRequest,
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key",
            min_length=16,
            max_length=128,
            pattern=r"^[A-Za-z0-9._:-]+$",
        ),
    ],
    _token: Annotated[str, Depends(require_operator)],
) -> JSONResponse:
    service = _service(request)
    try:
        run_id = service.request_refresh(
            body.collection,
            "operator",
            idempotency_key,
            requested_by="operator",
        )
    except IdempotencyConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency key conflict",
        ) from exc
    current = service.get_status(run_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Run status unavailable",
        )
    return _response(
        IngestionRunStatus.model_validate(current),
        status_code=status.HTTP_202_ACCEPTED,
    )


@router.get("/ingestion-runs/{ingestion_run_id}", response_model=IngestionRunStatus)
def get_ingestion_run(
    request: Request,
    ingestion_run_id: UUID,
    _token: Annotated[str, Depends(require_operator)],
) -> IngestionRunStatus:
    current = _service(request).get_status(ingestion_run_id)
    if current is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return IngestionRunStatus.model_validate(current)
