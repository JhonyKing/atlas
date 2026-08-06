"""Authenticated private-resource listing and repeat-safe deletion."""

from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Header, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from atlas.auth.service import SessionService
from atlas.privacy.deletion import DeletionIdempotencyConflict, IdempotentDeletionService
from atlas.privacy.ownership import InMemoryOwnershipService, ResourceNotFound

router = APIRouter(prefix="/v1/private", tags=["Private data"])


class PrivateResourceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resource_id: UUID
    resource_type: str
    metadata: dict[str, object]
    created_at: str


class PrivateResourceList(BaseModel):
    items: list[PrivateResourceItem]


def _token(request: Request, authorization: str | None) -> str | None:
    cookie = request.cookies.get("atlas_session")
    if cookie:
        return cookie
    if authorization and authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip() or None
    return None


def _subject(request: Request, authorization: str | None) -> UUID | None:
    service = cast(SessionService | None, request.app.state.auth_service)
    token = _token(request, authorization)
    if service is None or token is None:
        return None
    try:
        return service.current(token).subject_id
    except Exception:
        return None


def _service(request: Request) -> InMemoryOwnershipService | None:
    return cast(InMemoryOwnershipService | None, request.app.state.private_resource_service)


def _deletion(request: Request) -> IdempotentDeletionService | None:
    return cast(IdempotentDeletionService | None, request.app.state.private_deletion_service)


def _unauthorized() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Authentication required"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/resources", response_model=PrivateResourceList)
def list_private_resources(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> PrivateResourceList | JSONResponse:
    subject_id = _subject(request, authorization)
    service = _service(request)
    if subject_id is None:
        return _unauthorized()
    if service is None:
        return JSONResponse(status_code=503, content={"detail": "Private data unavailable"})
    return PrivateResourceList(
        items=[
            PrivateResourceItem(
                resource_id=item.resource_id,
                resource_type=item.resource_type,
                metadata=item.metadata,
                created_at=item.created_at.isoformat(),
            )
            for item in service.list_owned(subject_id)
        ]
    )


@router.delete("/resources/{resource_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_private_resource(
    resource_id: UUID,
    request: Request,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    subject_id = _subject(request, authorization)
    deletion = _deletion(request)
    if subject_id is None:
        return _unauthorized()
    if deletion is None:
        return JSONResponse(status_code=503, content={"detail": "Private data unavailable"})
    key = idempotency_key or f"resource-delete-{resource_id}"
    try:
        deletion.request(subject_id, resource_id, key)
    except DeletionIdempotencyConflict:
        return JSONResponse(status_code=409, content={"detail": "Idempotency key conflict"})
    except ResourceNotFound:
        return JSONResponse(status_code=404, content={"detail": "Private resource not found"})
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"status": "deletion_accepted"},
    )
