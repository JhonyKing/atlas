"""Deterministic model selection with Luna as the safe default."""

from __future__ import annotations

from atlas.config import Settings
from atlas.models.contracts import ModelSelection, ReasoningEffort, TaskSignals

APPROVED_MODELS = {"gpt-5.6-luna", "gpt-5.6-sol", "claude-sonnet"}


class ModelRouter:
    def __init__(self, settings: Settings, *, approved_models: set[str] | None = None) -> None:
        self._settings = settings
        self._approved = approved_models or APPROVED_MODELS

    def select(self, signals: TaskSignals) -> ModelSelection:
        model = self._settings.atlas_answer_model
        if model not in self._approved:
            raise ValueError("configured model is not approved")
        effort = self._effort(signals)
        reason = (
            f"{signals.kind}:{signals.complexity}:fresh={signals.freshness_required}:"
            f"contradiction={signals.contradiction_detected}"
        )
        return ModelSelection("openai", model, effort, "router-v1", reason)

    @staticmethod
    def _effort(signals: TaskSignals) -> ReasoningEffort:
        if signals.contradiction_detected or signals.report_depth == "deep":
            return "high"
        if signals.complexity == "low" and not signals.freshness_required:
            return "low"
        return "medium"
