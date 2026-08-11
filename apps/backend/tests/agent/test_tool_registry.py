from atlas.agent.tools.catalog import filter_catalog
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import ToolDefinition, ToolLocalization


def test_catalog_has_versioned_localized_allowlist() -> None:
    catalog = ToolCatalog.default()
    assert catalog.version == "1.0.0"
    assert {tool.tool_id for tool in catalog.tools} >= {
        "cited_answer",
        "comparison",
        "report",
        "daily_news",
        "corpus_status",
        "private_resources",
        "private_upload",
        "private_delete",
        "human_review",
    }
    assert all(
        "en-US" in tool.localization and "es-MX" in tool.localization for tool in catalog.tools
    )
    assert all(tool.input_schema["type"] == "object" for tool in catalog.tools)
    assert len(filter_catalog(catalog, locale="es-MX")) == len(catalog.tools)


def test_registry_rejects_unknown_fields() -> None:
    try:
        ToolDefinition(
            tool_id="example_tool",
            version="1.0.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            side_effect_level="read",
            approval="none",
            timeout_ms=1000,
            budget={"max_calls": 1},
            localization={
                "en-US": ToolLocalization(name="Example", description="Example"),
                "es-MX": ToolLocalization(name="Ejemplo", description="Ejemplo"),
            },
            unexpected="nope",  # type: ignore[call-arg]
        )
    except ValueError:
        return
    raise AssertionError("registry must reject unknown fields")
