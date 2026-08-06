"""Typed request dependencies shared by authenticated and anonymous routes."""

from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from fastapi import Header, Request

from atlas.auth.ports import AuthError, AuthPort


def _bearer_or_cookie(request: Request, authorization: str | None) -> str | None:
    cookie = request.cookies.get("atlas_session")
    if cookie:
        return cookie
    if authorization and authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip() or None
    return None


def optional_subject_id(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> UUID | None:
    """Return the authenticated subject, or None for the unchanged anonymous journey."""

    provider = cast(AuthPort | None, request.app.state.auth_provider)
    token = _bearer_or_cookie(request, authorization)
    if provider is None or token is None:
        return None
    try:
        return provider.validate(token).subject_id
    except AuthError:
        return None
