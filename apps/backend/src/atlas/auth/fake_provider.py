"""Deterministic in-memory AuthPort adapter for local development and tests."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from atlas.auth.ports import AuthError, AuthPort, AuthSession, IssuedSession, utc_now


@dataclass(slots=True)
class _StoredSession:
    session: AuthSession
    token_hash: str


class FakeAuthProvider(AuthPort):
    """Small local adapter that behaves like a revocable opaque-token provider."""

    def __init__(
        self,
        users: dict[str, tuple[str, UUID | None]],
        *,
        ttl: timedelta = timedelta(hours=8),
    ) -> None:
        self._users = {
            email.casefold(): (password, subject_id or uuid4())
            for email, (password, subject_id) in users.items()
        }
        self._ttl = ttl
        self._sessions: dict[str, _StoredSession] = {}

    def login(
        self,
        email: str,
        password: str,
        *,
        now: datetime | None = None,
    ) -> IssuedSession:
        credentials = self._users.get(email.casefold())
        if credentials is None or not secrets.compare_digest(credentials[0], password):
            raise AuthError("invalid credentials")
        return self._issue(credentials[1], now=now)

    def validate(self, access_token: str, *, now: datetime | None = None) -> AuthSession:
        stored = self._sessions.get(self._hash(access_token))
        if stored is None:
            raise AuthError("invalid session")
        current = utc_now(now)
        if stored.session.revoked_at is not None:
            raise AuthError("revoked session")
        if current >= stored.session.expires_at:
            raise AuthError("expired session")
        return stored.session

    def renew(self, access_token: str, *, now: datetime | None = None) -> IssuedSession:
        session = self.validate(access_token, now=now)
        self.revoke(access_token, now=now)
        return self._issue(session.subject_id, now=now)

    def revoke(self, access_token: str, *, now: datetime | None = None) -> bool:
        stored = self._sessions.get(self._hash(access_token))
        if stored is None or stored.session.revoked_at is not None:
            return False
        revoked_at = utc_now(now)
        stored.session = AuthSession(
            session_id=stored.session.session_id,
            subject_id=stored.session.subject_id,
            issued_at=stored.session.issued_at,
            expires_at=stored.session.expires_at,
            revoked_at=revoked_at,
        )
        return True

    def _issue(self, subject_id: UUID, *, now: datetime | None = None) -> IssuedSession:
        issued_at = utc_now(now)
        session = AuthSession(
            session_id=uuid4(),
            subject_id=subject_id,
            issued_at=issued_at,
            expires_at=issued_at + self._ttl,
        )
        access_token = secrets.token_urlsafe(32)
        self._sessions[self._hash(access_token)] = _StoredSession(
            session=session,
            token_hash=self._hash(access_token),
        )
        return IssuedSession(access_token=access_token, session=session)

    @staticmethod
    def _hash(access_token: str) -> str:
        return hashlib.sha256(access_token.encode("utf-8")).hexdigest()
