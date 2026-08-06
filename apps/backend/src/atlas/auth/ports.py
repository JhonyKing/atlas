"""Narrow contracts for authentication providers and session management."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID


class AuthError(ValueError):
    """Safe, user-facing authentication failure without provider-specific details."""


@dataclass(frozen=True, slots=True)
class AuthSession:
    """Validated session metadata; the raw bearer token is never part of this object."""

    session_id: UUID
    subject_id: UUID
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None

    @property
    def active(self) -> bool:
        """Return whether the session has not been explicitly revoked."""

        return self.revoked_at is None


@dataclass(frozen=True, slots=True)
class IssuedSession:
    """Token returned only at the authentication boundary, with a redacted representation."""

    access_token: str
    session: AuthSession

    def __repr__(self) -> str:
        return (
            "IssuedSession(access_token='[REDACTED]', "
            f"session_id={self.session.session_id!s})"
        )


class AuthPort(Protocol):
    """Provider-neutral authentication/session contract used by API code."""

    def login(
        self,
        email: str,
        password: str,
        *,
        now: datetime | None = None,
    ) -> IssuedSession: ...

    def validate(self, access_token: str, *, now: datetime | None = None) -> AuthSession: ...

    def renew(self, access_token: str, *, now: datetime | None = None) -> IssuedSession: ...

    def revoke(self, access_token: str, *, now: datetime | None = None) -> bool: ...

    def revoke_subject(self, subject_id: UUID, *, now: datetime | None = None) -> int: ...

    def get_locale(self, subject_id: UUID) -> str: ...

    def set_locale(self, subject_id: UUID, locale: str) -> str: ...

    def subject_for_token(self, access_token: str) -> UUID: ...


def utc_now(value: datetime | None = None) -> datetime:
    """Normalize optional clock input for deterministic tests."""

    current = value or datetime.now(UTC)
    if current.tzinfo is None:
        return current.replace(tzinfo=UTC)
    return current.astimezone(UTC)
