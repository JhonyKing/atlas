"""Public cited-answer HTTP and SSE contract."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from datetime import UTC, date, datetime
from typing import Annotated, Literal, Protocol, cast
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from atlas.domain import CollectionSlug, Question
from atlas.observability.context import current_request_id
from atlas.persistence.quota import QuotaExceeded

router = APIRouter(prefix="/v1/answers", tags=["Answers"])


class AskQuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: Annotated[str, Field(min_length=3, max_length=2000)]
    product: CollectionSlug | None = None
    version: Annotated[str, Field(max_length=64)] | None = None
    date_from: date | None = None
    date_to: date | None = None
    language: Literal["en-US", "es-MX"] | None = None


AnswerStatusValue = Literal[
    "accepted",
    "retrieving",
    "composing",
    "verifying",
    "completed",
    "abstained",
    "cancelling",
    "cancelled",
    "failed",
]


class AnswerRunStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    status: AnswerStatusValue
    created_at: datetime
    completed_at: datetime | None = None
    answer_status: Literal["complete", "partial", "abstained"] | None = None
    claims: list[dict[str, object]] = Field(default_factory=list)
    citations: list[dict[str, object]] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    retained_until: datetime | None = None


class AnswerRunConflict(RuntimeError):
    """Cancellation cannot change a terminal run."""


class AnswerRunControl(Protocol):
    async def start(
        self,
        *,
        question: Mapping[str, object],
        visitor_key_hash: str,
        idempotency_key: str,
        request_id: UUID,
    ) -> UUID: ...

    async def get_status(
        self,
        run_id: UUID,
        *,
        visitor_key_hash: str,
    ) -> AnswerRunStatus | None: ...

    async def cancel(self, run_id: UUID, *, visitor_key_hash: str) -> AnswerRunStatus: ...

    def stream(self, run_id: UUID, *, visitor_key_hash: str) -> AsyncIterator[str]: ...


def _service(request: Request) -> AnswerRunControl:
    service = request.app.state.answer_service
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Answer service is unavailable",
        )
    return cast(AnswerRunControl, service)


def _visitor_hash(request: Request) -> str:
    return getattr(request.state, "visitor_key_hash", "development-anonymous-visitor")


def _request_id(request: Request) -> UUID:
    return current_request_id() or UUID(int=0)


def _problem(
    request: Request,
    *,
    status_code: int,
    detail: str,
    error_code: str,
    entered_text: str | None = None,
    extra: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    payload: dict[str, object] = {
        "type": "about:blank",
        "title": detail,
        "status": status_code,
        "detail": detail,
        "request_id": str(_request_id(request)),
        "error_code": error_code,
    }
    if entered_text is not None:
        payload["entered_text"] = entered_text
    payload.update(extra or {})
    return JSONResponse(
        status_code=status_code,
        content=payload,
        media_type="application/problem+json",
        headers={"X-Request-ID": str(_request_id(request)), **(headers or {})},
    )


@router.post("", response_class=StreamingResponse, response_model=None)
async def create_answer(
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
    entered_text = raw_body.get("question")
    entered_text = entered_text if isinstance(entered_text, str) else ""
    try:
        body = AskQuestionRequest.model_validate(raw_body)
        if body.question.count("?") > 1:
            raise ValueError("submit one related question at a time")
        language = body.language or _language_from_request(request)
        question = Question(
            text=body.question,
            product=body.product,
            version=body.version,
            date_from=body.date_from,
            date_to=body.date_to,
            language=language,
        )
    except (ValidationError, ValueError) as exc:
        detail = str(exc) if isinstance(exc, ValueError) else "Question is not valid"
        return _problem(
            request,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="invalid_question",
            entered_text=entered_text,
        )

    service = _service(request)
    request_id = _request_id(request)
    try:
        run_id = await service.start(
            question=question.model_dump(mode="json"),
            visitor_key_hash=_visitor_hash(request),
            idempotency_key=idempotency_key,
            request_id=request_id,
        )
    except KeyError:
        return _problem(
            request,
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency key conflicts with another question",
            error_code="idempotency_conflict",
        )
    except TimeoutError:
        return _problem(
            request,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Answer service is unavailable",
            error_code="provider_unavailable",
        )
    except QuotaExceeded as exc:
        retry_after = exc.retry_after_seconds(now=datetime.now(UTC))
        return _problem(
            request,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Anonymous answer quota exceeded",
            error_code="quota_exceeded",
            extra={"retry_at": exc.retry_at.isoformat()},
            headers={"Retry-After": str(retry_after)},
        )

    async def stream() -> AsyncIterator[str]:
        async for frame in service.stream(run_id, visitor_key_hash=_visitor_hash(request)):
            yield frame

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "X-Atlas-Run-ID": str(run_id),
            "X-Request-ID": str(request_id),
            "Cache-Control": "no-cache",
        },
    )


def _language_from_request(request: Request) -> Literal["en-US", "es-MX"]:
    """Resolve explicit locale first, then the browser's Accept-Language header."""

    header = request.headers.get("accept-language", "").lower()
    return "es-MX" if header.startswith("es") else "en-US"


@router.get("/{run_id}")
async def get_answer(request: Request, run_id: UUID) -> JSONResponse:
    status_value = await _service(request).get_status(
        run_id,
        visitor_key_hash=_visitor_hash(request),
    )
    if status_value is None:
        return _problem(
            request,
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer run was not found",
            error_code="not_found",
        )
    response_status = (
        status.HTTP_202_ACCEPTED
        if status_value.status
        in {"accepted", "retrieving", "composing", "verifying", "cancelling"}
        else status.HTTP_200_OK
    )
    return JSONResponse(
        status_code=response_status,
        content=status_value.model_dump(mode="json"),
        headers={"X-Request-ID": str(_request_id(request))},
    )


@router.delete("/{run_id}")
async def cancel_answer(request: Request, run_id: UUID) -> JSONResponse:
    try:
        status_value = await _service(request).cancel(
            run_id,
            visitor_key_hash=_visitor_hash(request),
        )
    except KeyError:
        return _problem(
            request,
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer run was not found",
            error_code="not_found",
        )
    except AnswerRunConflict as exc:
        return _problem(
            request,
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
            error_code="conflict",
        )
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=status_value.model_dump(mode="json"),
        headers={"X-Request-ID": str(_request_id(request))},
    )
