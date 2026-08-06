"""Typed SQLAlchemy identity models matching migrations 0018-0020."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import CHAR


class IdentityBase(DeclarativeBase):
    pass


class UserModel(IdentityBase):
    __tablename__ = "users"
    __table_args__: ClassVar[dict[str, str]] = {"schema": "atlas"}  # type: ignore[misc]

    id: Mapped[UUID] = mapped_column(primary_key=True)
    auth_subject: Mapped[str] = mapped_column(Text, unique=True)
    locale: Mapped[str] = mapped_column(String(5), default="en-US")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SessionModel(IdentityBase):
    __tablename__ = "sessions"
    __table_args__: ClassVar[dict[str, str]] = {"schema": "atlas"}  # type: ignore[misc]

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("atlas.users.id", ondelete="CASCADE"))
    token_digest: Mapped[str] = mapped_column(CHAR(64), unique=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    device_label: Mapped[str | None] = mapped_column(String(120))


class OwnershipGrantModel(IdentityBase):
    __tablename__ = "ownership_grants"
    __table_args__ = (
        UniqueConstraint("user_id", "resource_type", "resource_id"),
        {"schema": "atlas"},
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("atlas.users.id", ondelete="CASCADE"), primary_key=True
    )
    resource_type: Mapped[str] = mapped_column(String(32), primary_key=True)
    resource_id: Mapped[UUID] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
