"""Explicit consent and no-training policy for private documents."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ConsentRecord:
    subject_id: UUID
    scope: str
    locale: str
    policy_version: str
    granted_at: datetime
    withdrawn_at: datetime | None = None

    @property
    def active(self) -> bool:
        return self.withdrawn_at is None


def grant_consent(
    subject_id: UUID, *, scope: str, locale: str, policy_version: str
) -> ConsentRecord:
    if locale not in {"en-US", "es-MX"}:
        raise ValueError("unsupported locale")
    if not scope.strip() or not policy_version.strip():
        raise ValueError("scope and policy version are required")
    return ConsentRecord(subject_id, scope, locale, policy_version, datetime.now(UTC))


def withdraw_consent(record: ConsentRecord) -> ConsentRecord:
    if not record.active:
        return record
    return ConsentRecord(
        record.subject_id,
        record.scope,
        record.locale,
        record.policy_version,
        record.granted_at,
        datetime.now(UTC),
    )


def assert_private_not_promoted(*, provenance: str, tenant_id: UUID | None) -> None:
    if provenance == "private_upload" and tenant_id is None:
        raise ValueError("private content requires a tenant boundary")
