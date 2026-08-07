"""Versioned allowlist of capabilities that the ATLAS agent may invoke."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Locale = Literal["en-US", "es-MX"]
SideEffectLevel = Literal["read", "private_read", "mutate", "publish", "delete"]
ApprovalMode = Literal["none", "explicit_user", "human_reviewer"]
Availability = Literal["enabled", "disabled", "provider_unavailable", "quota_exhausted"]


class ToolLocalization(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=500)


class ToolDefinition(BaseModel):
    """Public metadata and policy for one callable ATLAS capability.

    The model is intentionally provider-neutral. A model-generated tool name or argument object
    must be validated against this record before an executor is allowed to call a domain service.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    tool_id: str = Field(pattern=r"^[a-z][a-z0-9_]{2,63}$")
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    input_schema: dict[str, object]
    output_schema: dict[str, object]
    scopes: tuple[str, ...] = ()
    side_effect_level: SideEffectLevel
    approval: ApprovalMode
    timeout_ms: int = Field(gt=0, le=120_000)
    budget: dict[str, int]
    localization: dict[Locale, ToolLocalization]
    availability: Availability = "enabled"


class ToolCatalog(BaseModel):
    """The immutable registry exposed to both the API and the agent planner."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    tools: tuple[ToolDefinition, ...]

    def list_for_locale(self, locale: Locale) -> tuple[ToolDefinition, ...]:
        """Return only definitions with copy for the requested locale."""

        return tuple(tool for tool in self.tools if locale in tool.localization)

    def get(self, tool_id: str) -> ToolDefinition | None:
        return next((tool for tool in self.tools if tool.tool_id == tool_id), None)

    @classmethod
    def default(cls) -> ToolCatalog:
        """Build the initial catalog from domain capabilities already present in ATLAS."""

        return cls(
            version="1.0.0",
            tools=(
                _read_tool(
                    "cited_answer",
                    "Cited answer",
                    "Ask one technical question and receive evidence-checked claims.",
                    "Respuesta con citas",
                    "Haz una pregunta técnica y recibe afirmaciones comprobadas con evidencia.",
                ),
                _read_tool(
                    "comparison",
                    "Technology comparison",
                    "Compare two to four technologies with evidence per criterion.",
                    "Comparación de tecnologías",
                    "Compara de dos a cuatro tecnologías con evidencia por criterio.",
                    deep=True,
                ),
                _read_tool(
                    "report",
                    "Generate report",
                    "Create a cited report or document from a verified research result.",
                    "Generar reporte",
                    "Crea un reporte o documento con citas a partir de una investigación "
                    "verificada.",
                    deep=True,
                ),
                _read_tool(
                    "daily_news",
                    "Previous-day news",
                    "Retrieve the previous day's most important attributable internet signal.",
                    "Noticia del día anterior",
                    "Recupera la noticia atribuible más importante del día anterior en Internet.",
                ),
                _read_tool(
                    "corpus_status",
                    "Corpus status",
                    "Inspect source collections, freshness, coverage, and verification status.",
                    "Estado del corpus",
                    "Consulta colecciones, actualización, cobertura y estado de verificación.",
                ),
                _private_tool(
                    "private_resources",
                    "Private resources",
                    "List private resources owned by the authenticated user.",
                    "Recursos privados",
                    "Lista los recursos privados de la persona autenticada.",
                    side_effect_level="private_read",
                    approval="explicit_user",
                ),
                _private_tool(
                    "private_upload",
                    "Upload private resource",
                    "Upload and govern a private document for the authenticated user.",
                    "Subir recurso privado",
                    "Sube y gobierna un documento privado de la persona autenticada.",
                    side_effect_level="mutate",
                    approval="explicit_user",
                ),
                _private_tool(
                    "private_delete",
                    "Delete private resource",
                    "Delete an owned private resource and its derived data repeat-safely.",
                    "Eliminar recurso privado",
                    "Elimina un recurso privado propio y sus datos derivados de forma repetible.",
                    side_effect_level="delete",
                    approval="explicit_user",
                ),
                _private_tool(
                    "human_review",
                    "Human review",
                    "Approve, edit, or reject a consequential publication decision.",
                    "Revisión humana",
                    "Aprueba, edita o rechaza una decisión de publicación relevante.",
                    side_effect_level="publish",
                    approval="human_reviewer",
                ),
            ),
        )


def _read_tool(
    tool_id: str,
    name: str,
    description: str,
    spanish_name: str,
    spanish_description: str,
    *,
    deep: bool = False,
) -> ToolDefinition:
    return ToolDefinition(
        tool_id=tool_id,
        version="1.0.0",
        input_schema={"type": "object", "additionalProperties": False},
        output_schema={"type": "object", "additionalProperties": False},
        side_effect_level="read",
        approval="none",
        timeout_ms=30_000 if deep else 15_000,
        budget={"max_calls": 1, "max_evidence": 32 if deep else 16},
        localization={
            "en-US": ToolLocalization(name=name, description=description),
            "es-MX": ToolLocalization(name=spanish_name, description=spanish_description),
        },
    )


def _private_tool(
    tool_id: str,
    name: str,
    description: str,
    spanish_name: str,
    spanish_description: str,
    *,
    side_effect_level: SideEffectLevel,
    approval: ApprovalMode,
) -> ToolDefinition:
    return ToolDefinition(
        tool_id=tool_id,
        version="1.0.0",
        input_schema={"type": "object", "additionalProperties": False},
        output_schema={"type": "object", "additionalProperties": False},
        scopes=("authenticated",),
        side_effect_level=side_effect_level,
        approval=approval,
        timeout_ms=15_000,
        budget={"max_calls": 1, "max_evidence": 8},
        localization={
            "en-US": ToolLocalization(name=name, description=description),
            "es-MX": ToolLocalization(name=spanish_name, description=spanish_description),
        },
    )
