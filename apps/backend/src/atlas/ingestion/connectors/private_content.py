"""Tenant-scoped private content connector; never promotes to public corpus."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class PrivateConnectorRecord:
    source_id: UUID
    owner_id: UUID
    filename: str
    content_sha256: str
    private: bool = True
    public_promoted: bool = False


class PrivateContentConnector:
    def __init__(self, *, owner_id: UUID) -> None:
        self._owner_id = owner_id

    def accept(self, subject_id: UUID, *, filename: str, content: bytes) -> PrivateConnectorRecord:
        if subject_id != self._owner_id:
            raise PermissionError("private source not found")
        if not filename or not content:
            raise ValueError("private source requires filename and content")
        return PrivateConnectorRecord(
            uuid4(), subject_id, filename, hashlib.sha256(content).hexdigest()
        )
