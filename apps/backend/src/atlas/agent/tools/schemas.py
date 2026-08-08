"""Strict, provider-neutral schemas for the ATLAS tool registry."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

JsonType = dict[str, object]
SideEffectLevel = Literal["read", "private_read", "mutate", "publish", "delete"]
ApprovalMode = Literal["none", "explicit_user", "human_reviewer"]
Availability = Literal["enabled", "disabled", "provider_unavailable", "quota_exhausted"]
Locale = Literal["en-US", "es-MX"]


class ToolLocalization(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=500)


class ToolDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    tool_id: str = Field(pattern=r"^[a-z][a-z0-9_]{2,63}$")
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    input_schema: JsonType
    output_schema: JsonType
    scopes: tuple[str, ...] = ()
    side_effect_level: SideEffectLevel
    approval: ApprovalMode
    timeout_ms: int = Field(gt=0, le=120_000)
    budget: dict[str, int]
    localization: dict[Locale, ToolLocalization]
    availability: Availability = "enabled"


class ToolCallRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_id: str = Field(pattern=r"^[a-z][a-z0-9_]{2,63}$")
    tool_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    arguments: dict[str, object] = Field(default_factory=dict)
    dependencies: tuple[str, ...] = ()
    expected_output: str = Field(default="tool_result", min_length=1, max_length=120)


def validate_json_object(
    value: Mapping[str, object], schema: Mapping[str, object]
) -> dict[str, object]:
    """Validate the bounded object subset used by catalog input schemas."""

    if schema.get("type") != "object":
        raise ValueError("tool schema must describe an object")
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    if not isinstance(properties, dict) or not isinstance(required, list):
        raise ValueError("tool schema properties and required must be arrays/objects")
    if schema.get("additionalProperties") is False:
        unknown = set(value) - set(properties)
        if unknown:
            raise ValueError(f"unknown tool arguments: {', '.join(sorted(unknown))}")
    missing = {str(name) for name in required if name not in value}
    if missing:
        raise ValueError(f"missing tool arguments: {', '.join(sorted(missing))}")
    for name, definition in properties.items():
        if name not in value or not isinstance(definition, dict):
            continue
        expected = definition.get("type")
        current = value[name]
        valid = (
            (expected != "string" or isinstance(current, str))
            and (expected != "array" or isinstance(current, list))
            and (
                expected != "integer"
                or (isinstance(current, int) and not isinstance(current, bool))
            )
            and (expected != "boolean" or isinstance(current, bool))
        )
        if not valid:
            raise ValueError(f"invalid type for tool argument {name}")
        enum = definition.get("enum")
        if isinstance(enum, list) and current not in enum:
            raise ValueError(f"invalid value for tool argument {name}")
    return dict(value)
