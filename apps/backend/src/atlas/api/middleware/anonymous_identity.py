"""Privacy-preserving anonymous visitor identity middleware."""

from __future__ import annotations

import hashlib
import hmac
import secrets

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

VISITOR_COOKIE_NAME = "atlas_visitor"
VISITOR_TOKEN_HEADER = "X-Atlas-Visitor-Token"
VISITOR_COOKIE_MAX_AGE = 60 * 60 * 24 * 30
_MIN_COOKIE_LENGTH = 32
_MAX_COOKIE_LENGTH = 256


def visitor_key_hash(secret: str, raw_cookie: str) -> str:
    """Derive the only visitor identifier allowed to cross the persistence boundary."""

    if not secret.strip():
        raise ValueError("visitor HMAC secret must not be empty")
    if not _MIN_COOKIE_LENGTH <= len(raw_cookie) <= _MAX_COOKIE_LENGTH:
        raise ValueError("visitor cookie has an invalid length")
    return hmac.new(
        secret.encode("utf-8"),
        raw_cookie.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


class AnonymousIdentityMiddleware(BaseHTTPMiddleware):
    """Issue an opaque cookie and expose only its HMAC digest on request state."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        secret: str,
        cookie_max_age: int = VISITOR_COOKIE_MAX_AGE,
    ) -> None:
        super().__init__(app)
        if not secret.strip():
            raise ValueError("visitor HMAC secret must not be empty")
        if cookie_max_age <= 0:
            raise ValueError("cookie_max_age must be positive")
        self._secret = secret
        self._cookie_max_age = cookie_max_age

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        cookie_token = request.cookies.get(VISITOR_COOKIE_NAME)
        header_token = request.headers.get(VISITOR_TOKEN_HEADER)
        supplied_token = header_token if self._is_valid_cookie(header_token) else cookie_token
        issue_cookie = supplied_token is None or not self._is_valid_cookie(supplied_token)
        if header_token is not None and self._is_valid_cookie(header_token):
            issue_cookie = cookie_token != header_token
        raw_cookie = supplied_token
        if issue_cookie:
            raw_cookie = secrets.token_urlsafe(32)
        assert raw_cookie is not None
        request.state.visitor_key_hash = visitor_key_hash(self._secret, raw_cookie)

        response = await call_next(request)
        response.headers[VISITOR_TOKEN_HEADER] = raw_cookie
        if issue_cookie:
            response.set_cookie(
                VISITOR_COOKIE_NAME,
                raw_cookie,
                max_age=self._cookie_max_age,
                httponly=True,
                secure=True,
                samesite="lax",
            )
        return response

    @staticmethod
    def _is_valid_cookie(raw_cookie: str | None) -> bool:
        return raw_cookie is not None and _MIN_COOKIE_LENGTH <= len(raw_cookie) <= (
            _MAX_COOKIE_LENGTH
        )
