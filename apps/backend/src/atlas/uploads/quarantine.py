"""In-memory quarantine adapter used by local tests before object storage integration."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class QuarantinedObject:
    object_id: UUID
    owner_id: UUID
    filename: str
    content_type: str
    content: bytes


class QuarantineStore:
    def __init__(self) -> None:
        self._objects: dict[UUID, QuarantinedObject] = {}

    def put(
        self,
        owner_id: UUID,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> QuarantinedObject:
        object_value = QuarantinedObject(uuid4(), owner_id, filename, content_type, content)
        self._objects[object_value.object_id] = object_value
        return object_value

    def get(self, object_id: UUID) -> QuarantinedObject:
        return self._objects[object_id]

    def delete(self, object_id: UUID) -> None:
        self._objects.pop(object_id, None)
