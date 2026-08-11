"""Typed, allowlisted agent tool contracts."""

from atlas.agent.tools.read_only import is_read_only_tool
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import ToolCallRequest, ToolDefinition, ToolLocalization

__all__ = [
    "ToolCallRequest",
    "ToolCatalog",
    "ToolDefinition",
    "ToolLocalization",
    "is_read_only_tool",
    "requires_explicit_approval",
]


def __getattr__(name: str) -> object:
    if name == "requires_explicit_approval":
        from atlas.agent.tools.side_effects import requires_explicit_approval

        return requires_explicit_approval
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
