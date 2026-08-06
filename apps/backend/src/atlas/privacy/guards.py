"""Reusable application-level ownership guards."""

from __future__ import annotations

from uuid import UUID

from atlas.privacy.ownership import InMemoryOwnershipService, PrivateResource


def require_owner(
    service: InMemoryOwnershipService,
    subject_id: UUID,
    resource_id: UUID,
) -> PrivateResource:
    """Resolve a resource only through its owner, avoiding cross-user disclosure."""

    return service.get_owned(subject_id, resource_id)
