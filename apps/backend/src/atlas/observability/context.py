"""Request-scoped identifiers shared by HTTP handlers, logs, and traces."""

from __future__ import annotations

from contextvars import ContextVar, Token
from uuid import UUID, uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"
_REQUEST_ID: ContextVar[UUID | None] = ContextVar("atlas_request_id", default=None)


def current_request_id() -> UUID | None:
    """Return the request identifier for the current async context, if one exists."""

    return _REQUEST_ID.get()


def _resolve_request_id(raw_value: str | None) -> UUID:
    if raw_value is not None:
        try:
            return UUID(raw_value)
        except ValueError:
            pass
    return uuid4()


def set_request_id(request_id: UUID) -> Token[UUID | None]:
    """Set a request ID and return the context token needed to restore the prior value."""

    return _REQUEST_ID.set(request_id)


def reset_request_id(token: Token[UUID | None]) -> None:
    """Restore the request ID that was active before a request context was entered."""

    _REQUEST_ID.reset(token)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Propagate one opaque UUID through a request and return it in the response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = _resolve_request_id(request.headers.get(REQUEST_ID_HEADER))
        token = set_request_id(request_id)
        try:
            response = await call_next(request)
            response.headers.setdefault(REQUEST_ID_HEADER, str(request_id))
            return response
        finally:
            reset_request_id(token)
