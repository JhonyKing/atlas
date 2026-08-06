"""Typed SQLAlchemy private-upload and deletion models."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BIGINT, CHAR

from atlas.auth.models import IdentityBase


class PrivateUploadModel(IdentityBase):
    __tablename__ = "private_uploads"
    __table_args__: ClassVar[dict[str, str]] = {"schema": "atlas"}  # type: ignore[misc]

    id: Mapped[UUID] = mapped_column(primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("atlas.users.id", ondelete="CASCADE"))
    storage_key: Mapped[str] = mapped_column(Text, unique=True)
    declared_content_type: Mapped[str] = mapped_column(String(160))
    detected_content_type: Mapped[str | None] = mapped_column(String(160))
    size_bytes: Mapped[int] = mapped_column(BIGINT)
    content_hash: Mapped[str | None] = mapped_column(CHAR(64))
    scan_status: Mapped[str] = mapped_column(String(16))
    parse_status: Mapped[str] = mapped_column(String(16))
    retention_until: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DeletionJobModel(IdentityBase):
    __tablename__ = "deletion_jobs"
    __table_args__: ClassVar[dict[str, str]] = {"schema": "atlas"}  # type: ignore[misc]

    id: Mapped[UUID] = mapped_column(primary_key=True)
    requested_by: Mapped[UUID] = mapped_column(ForeignKey("atlas.users.id", ondelete="CASCADE"))
    scope: Mapped[str] = mapped_column(String(16))
    resource_id: Mapped[UUID | None] = mapped_column()
    idempotency_key: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(16))
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(128))
