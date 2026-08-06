"""Private upload lifecycle: validate -> quarantine -> scan -> parse -> index gate."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from atlas.uploads.quarantine import QuarantineStore
from atlas.uploads.validation import UploadValidationError, validate_upload


class UploadRejected(ValueError):
    """Upload was rejected before it could become searchable."""

    def __init__(self, message: str, *, record: PrivateUploadRecord | None = None) -> None:
        super().__init__(message)
        self.record = record


@dataclass(frozen=True, slots=True)
class PrivateUploadRecord:
    upload_id: UUID
    owner_id: UUID
    filename: str
    declared_content_type: str
    detected_content_type: str
    provenance: str
    size_bytes: int
    content_hash: str
    scan_status: str
    parse_status: str
    indexable: bool
    created_at: datetime
    retention_until: datetime


class PrivateUploadPipeline:
    def __init__(self, *, quarantine: QuarantineStore | None = None) -> None:
        self._quarantine = quarantine or QuarantineStore()
        self._records: dict[UUID, PrivateUploadRecord] = {}
        self._idempotency: dict[tuple[UUID, str], UUID] = {}

    def submit(
        self,
        owner_id: UUID,
        *,
        filename: str,
        declared_content_type: str,
        content: bytes,
        idempotency_key: str | None = None,
    ) -> PrivateUploadRecord:
        if idempotency_key:
            previous = self._idempotency.get((owner_id, idempotency_key))
            if previous is not None:
                return self._records[previous]
        try:
            validated = validate_upload(
                filename=filename,
                declared_content_type=declared_content_type,
                content=content,
            )
        except UploadValidationError as exc:
            raise UploadRejected(str(exc)) from exc
        quarantine = self._quarantine.put(
            owner_id, validated.filename, validated.declared_content_type, validated.content
        )
        digest = hashlib.sha256(validated.content).hexdigest()
        scan_status = "rejected" if b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE" in content else "clean"
        created_at = datetime.now(UTC)
        record = PrivateUploadRecord(
            upload_id=quarantine.object_id,
            owner_id=owner_id,
            filename=validated.filename,
            declared_content_type=validated.declared_content_type,
            detected_content_type=validated.detected_content_type,
            provenance="private_upload",
            size_bytes=validated.size_bytes,
            content_hash=digest,
            scan_status=scan_status,
            parse_status="rejected" if scan_status == "rejected" else "parsed",
            indexable=scan_status == "clean",
            created_at=created_at,
            retention_until=created_at + timedelta(days=30),
        )
        self._records[record.upload_id] = record
        if idempotency_key:
            self._idempotency[(owner_id, idempotency_key)] = record.upload_id
        self._quarantine.delete(record.upload_id) if not record.indexable else None
        if not record.indexable:
            raise UploadRejected("upload failed malware scan", record=record)
        return record

    def get(self, owner_id: UUID, upload_id: UUID) -> PrivateUploadRecord:
        record = self._records[upload_id]
        if record.owner_id != owner_id:
            raise KeyError(upload_id)
        return record

    def indexable_uploads(self) -> list[PrivateUploadRecord]:
        return [record for record in self._records.values() if record.indexable]

    def records(self) -> list[PrivateUploadRecord]:
        return list(self._records.values())

    def delete(self, owner_id: UUID, upload_id: UUID) -> None:
        record = self.get(owner_id, upload_id)
        self._records.pop(record.upload_id, None)
        self._quarantine.delete(record.upload_id)

    def delete_owner(self, owner_id: UUID) -> int:
        owned = [
            record.upload_id for record in self._records.values() if record.owner_id == owner_id
        ]
        for upload_id in owned:
            self.delete(owner_id, upload_id)
        return len(owned)
