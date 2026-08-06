"""Application-level ownership boundary for authenticated private resources."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from threading import RLock
from typing import Any, Literal
from uuid import UUID, uuid4

ResourceType = Literal["thread", "report", "feedback", "artifact", "upload"]


class ResourceNotFound(KeyError):
    """Resource is absent or belongs to another subject."""

    def __init__(self, resource_id: UUID | None = None) -> None:
        del resource_id
        super().__init__("private resource not found")


@dataclass(frozen=True, slots=True)
class PrivateResource:
    resource_id: UUID
    owner_id: UUID
    resource_type: ResourceType
    metadata: dict[str, Any]
    created_at: datetime
    deleted_at: datetime | None = None


class InMemoryOwnershipService:
    """Deterministic ownership repository used until the PostgreSQL adapter is wired."""

    def __init__(self) -> None:
        self._resources: dict[UUID, PrivateResource] = {}
        self._lock = RLock()

    def create(
        self,
        owner_id: UUID,
        resource_type: ResourceType,
        metadata: dict[str, Any],
    ) -> PrivateResource:
        resource = PrivateResource(
            resource_id=uuid4(),
            owner_id=owner_id,
            resource_type=resource_type,
            metadata=dict(metadata),
            created_at=datetime.now(UTC),
        )
        with self._lock:
            self._resources[resource.resource_id] = resource
        return resource

    def list_owned(self, owner_id: UUID) -> list[PrivateResource]:
        with self._lock:
            return [
                resource
                for resource in self._resources.values()
                if resource.owner_id == owner_id and resource.deleted_at is None
            ]

    def get_owned(self, owner_id: UUID, resource_id: UUID) -> PrivateResource:
        with self._lock:
            resource = self._resources.get(resource_id)
            if resource is None or resource.owner_id != owner_id or resource.deleted_at is not None:
                raise ResourceNotFound(resource_id)
            return resource

    def delete_owned(self, owner_id: UUID, resource_id: UUID) -> bool:
        with self._lock:
            resource = self._resources.get(resource_id)
            if resource is None or resource.owner_id != owner_id:
                raise ResourceNotFound(resource_id)
            if resource.deleted_at is not None:
                return False
            self._resources[resource_id] = PrivateResource(
                resource_id=resource.resource_id,
                owner_id=resource.owner_id,
                resource_type=resource.resource_type,
                metadata=resource.metadata,
                created_at=resource.created_at,
                deleted_at=datetime.now(UTC),
            )
            return True

    def delete_all(self, owner_id: UUID) -> int:
        deleted = 0
        for resource in self.list_owned(owner_id):
            if self.delete_owned(owner_id, resource.resource_id):
                deleted += 1
        return deleted
