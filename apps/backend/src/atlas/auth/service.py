"""Application service that keeps API code independent from an auth provider SDK."""

from __future__ import annotations

from datetime import datetime

from atlas.auth.ports import AuthError, AuthPort, AuthSession, IssuedSession


class SessionService:
    """Use-case boundary for login, validation, renewal, and revocation."""

    def __init__(self, provider: AuthPort) -> None:
        self._provider = provider

    def login(
        self,
        email: str,
        password: str,
        *,
        now: datetime | None = None,
    ) -> IssuedSession:
        return self._provider.login(email, password, now=now)

    def current(self, access_token: str | None, *, now: datetime | None = None) -> AuthSession:
        if not access_token:
            raise AuthError("invalid session")
        return self._provider.validate(access_token, now=now)

    def renew(self, access_token: str | None, *, now: datetime | None = None) -> IssuedSession:
        if not access_token:
            raise AuthError("invalid session")
        return self._provider.renew(access_token, now=now)

    def logout(self, access_token: str | None, *, now: datetime | None = None) -> bool:
        if not access_token:
            return False
        return self._provider.revoke(access_token, now=now)
