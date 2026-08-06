"""Authenticated private-resource listing and repeat-safe deletion."""

from __future__ import annotations

import base64
import binascii
from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Header, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from atlas.auth.service import SessionService
from atlas.observability.events import record_security_event
from atlas.privacy.deletion import DeletionIdempotencyConflict, IdempotentDeletionService
from atlas.privacy.ownership import InMemoryOwnershipService, ResourceNotFound
from atlas.uploads.deletion import UploadDeletionService
from atlas.uploads.pipeline import PrivateUploadPipeline, UploadRejected

router = APIRouter(prefix="/v1/private", tags=["Private data"])


class PrivateResourceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resource_id: UUID
    resource_type: str
    metadata: dict[str, object]
    created_at: str


class PrivateResourceList(BaseModel):
    items: list[PrivateResourceItem]


class PrivateUploadRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str
    declared_content_type: str
    content_base64: str


class PrivateUploadResponse(BaseModel):
    upload_id: UUID
    filename: str
    detected_content_type: str
    provenance: str
    scan_status: str
    parse_status: str
    indexable: bool
    content_hash: str


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


def _uploads(request: Request) -> PrivateUploadPipeline | None:
    return cast(PrivateUploadPipeline | None, request.app.state.private_upload_pipeline)


def _upload_deletion(request: Request) -> UploadDeletionService | None:
    return cast(UploadDeletionService | None, request.app.state.private_upload_deletion)


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
    record_security_event(
        request,
        operation="private.resources.list",
        subject_id=subject_id,
        ownership_decision="owner_only",
    )
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
        record_security_event(
            request,
            operation="private.resource.delete.denied",
            subject_id=subject_id,
            ownership_decision="denied",
        )
        return JSONResponse(status_code=404, content={"detail": "Private resource not found"})
    record_security_event(
        request,
        operation="private.resource.delete.accepted",
        subject_id=subject_id,
        ownership_decision="owner_only",
    )
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"status": "deletion_accepted"},
    )


@router.post(
    "/uploads",
    response_model=PrivateUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_private_upload(
    body: PrivateUploadRequest,
    request: Request,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> PrivateUploadResponse | JSONResponse:
    subject_id = _subject(request, authorization)
    pipeline = _uploads(request)
    if subject_id is None:
        return _unauthorized()
    if pipeline is None:
        return JSONResponse(status_code=503, content={"detail": "Upload service unavailable"})
    if idempotency_key is None or len(idempotency_key.strip()) < 8:
        return JSONResponse(status_code=400, content={"detail": "Idempotency-Key is required"})
    try:
        content = base64.b64decode(body.content_base64, validate=True)
    except (ValueError, binascii.Error):
        return JSONResponse(status_code=400, content={"detail": "content_base64 is invalid"})
    try:
        record = pipeline.submit(
            subject_id,
            filename=body.filename,
            declared_content_type=body.declared_content_type,
            content=content,
            idempotency_key=idempotency_key,
        )
    except UploadRejected as exc:
        record_security_event(
            request,
            operation="private.upload.rejected",
            subject_id=subject_id,
            fields={"filename": body.filename, "content": "[omitted]"},
        )
        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc),
                "indexable": bool(exc.record and exc.record.indexable),
            },
        )
    record_security_event(
        request,
        operation="private.upload.accepted",
        subject_id=subject_id,
        fields={"filename": body.filename, "content_hash": record.content_hash},
    )
    return PrivateUploadResponse(
        upload_id=record.upload_id,
        filename=record.filename,
        detected_content_type=record.detected_content_type,
        provenance=record.provenance,
        scan_status=record.scan_status,
        parse_status=record.parse_status,
        indexable=record.indexable,
        content_hash=record.content_hash,
    )


@router.delete(
    "/uploads/{upload_id}",
    response_model=None,
    status_code=status.HTTP_202_ACCEPTED,
)
def delete_private_upload(
    upload_id: UUID,
    request: Request,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    subject_id = _subject(request, authorization)
    deletion = _upload_deletion(request)
    if subject_id is None:
        return _unauthorized()
    if deletion is None:
        return JSONResponse(status_code=503, content={"detail": "Upload service unavailable"})
    key = idempotency_key or f"upload-delete-{upload_id}"
    try:
        deletion.delete(subject_id, upload_id, key)
    except KeyError:
        return JSONResponse(status_code=404, content={"detail": "Private upload not found"})
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"status": "deleted"})
