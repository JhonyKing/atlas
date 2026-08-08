"""Identity, locale, beta, and provider-aware catalog filtering."""

from __future__ import annotations

from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import Locale, ToolDefinition


def filter_catalog(
    catalog: ToolCatalog,
    *,
    locale: Locale,
    scopes: set[str] | None = None,
    include_unavailable: bool = True,
    provider_ready: bool = True,
) -> tuple[ToolDefinition, ...]:
    """Return only tools the caller can understand and is allowed to see."""

    granted = scopes or {"anonymous"}
    result: list[ToolDefinition] = []
    for tool in catalog.list_for_locale(locale):
        if not include_unavailable and tool.availability != "enabled":
            continue
        if not provider_ready and "provider" in tool.scopes:
            continue
        required = set(tool.scopes)
        if required and not (required & granted) and "anonymous" not in granted:
            continue
        result.append(tool)
    return tuple(result)
