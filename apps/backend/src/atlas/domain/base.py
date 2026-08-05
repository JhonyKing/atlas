"""Shared configuration for provider-independent ATLAS domain contracts."""

from pydantic import BaseModel, ConfigDict


class DomainModel(BaseModel):
    """Reject silent coercion and unknown provider-specific fields."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        populate_by_name=True,
    )
