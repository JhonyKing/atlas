"""Optional authentication session endpoints."""

from __future__ import annotations

from typing import Annotated, cast

from fastapi import APIRouter, Header, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from atlas.auth.ports import AuthError, AuthPort, AuthSession

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])
SESSION_COOKIE = "atlas_session"


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Annotated[str, Field(min_length=3, max_length=320)]
    password: Annotated[str, Field(min_length=1)]


class SessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    subject_id: str
    issued_at: str
    expires_at: str

    @classmethod
    def from_session(cls, session: AuthSession) -> SessionResponse:
        return cls(
            session_id=str(session.session_id),
            subject_id=str(session.subject_id),
            issued_at=session.issued_at.isoformat(),
            expires_at=session.expires_at.isoformat(),
        )


def _provider(request: Request) -> AuthPort | None:
    return cast(AuthPort | None, request.app.state.auth_provider)


def _token(request: Request, authorization: str | None) -> str | None:
    cookie = request.cookies.get(SESSION_COOKIE)
    if cookie:
        return cookie
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        return token or None
    return None


def _auth_unavailable() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Authentication service is unavailable"},
    )


def _unauthorized() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Authentication required"},
        headers={"WWW-Authenticate": "Bearer"},
    )


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=8 * 60 * 60,
        path="/",
    )


@router.post("/session", response_model=SessionResponse)
def login(
    body: LoginRequest, request: Request, response: Response
) -> SessionResponse | JSONResponse:
    provider = _provider(request)
    if provider is None:
        return _auth_unavailable()
    try:
        issued = provider.login(str(body.email), body.password)
    except AuthError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials"},
        )
    _set_session_cookie(response, issued.access_token)
    return SessionResponse.from_session(issued.session)


@router.get("/session", response_model=SessionResponse)
def get_session(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> SessionResponse | JSONResponse:
    provider = _provider(request)
    token = _token(request, authorization)
    if provider is None:
        return _auth_unavailable()
    if token is None:
        return _unauthorized()
    try:
        session = provider.validate(token)
    except AuthError:
        return _unauthorized()
    return SessionResponse.from_session(session)


@router.post("/renew", response_model=SessionResponse)
def renew_session(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> SessionResponse | JSONResponse:
    provider = _provider(request)
    token = _token(request, authorization)
    if provider is None:
        return _auth_unavailable()
    if token is None:
        return _unauthorized()
    try:
        issued = provider.renew(token)
    except AuthError:
        return _unauthorized()
    _set_session_cookie(response, issued.access_token)
    return SessionResponse.from_session(issued.session)


@router.delete("/session", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> Response | JSONResponse:
    provider = _provider(request)
    token = _token(request, authorization)
    if provider is None:
        return _auth_unavailable()
    if token is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    provider.revoke(token)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
