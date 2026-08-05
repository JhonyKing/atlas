"""Safe local comparison executor used only for the bounded development demo."""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from atlas.comparison.schemas import (
    ComparisonCell,
    ComparisonCellState,
    ComparisonCriterion,
    ComparisonMatrix,
    ComparisonRequest,
)
from atlas.demo import DemoAnswerGraph


class DemoComparisonExecutor:
    """Return explicitly labelled local facts; never represents them as production corpus data."""

    async def run(
        self,
        comparison: ComparisonRequest,
        *,
        snapshot_id: UUID,
        is_cancelled: Callable[[], bool],
    ) -> ComparisonMatrix:
        del snapshot_id
        cells: list[ComparisonCell] = []
        for technology in comparison.technologies:
            if is_cancelled():
                raise RuntimeError("comparison was cancelled")
            for criterion in comparison.criteria:
                if criterion is ComparisonCriterion.CAPABILITY:
                    evidence = DemoAnswerGraph._evidence(technology)
                    cells.append(
                        ComparisonCell(
                            technology_id=technology,
                            criterion_id=criterion,
                            state=ComparisonCellState.SUPPORTED,
                            value="Documented capability in the local demo corpus",
                            explanation=(
                                "Development-only fixture; replace with a verified corpus "
                                "snapshot before production use."
                            ),
                            evidence_ids=[evidence.id],
                            observed_at=evidence.captured_at,
                        )
                    )
                else:
                    cells.append(
                        ComparisonCell(
                            technology_id=technology,
                            criterion_id=criterion,
                            state=ComparisonCellState.UNSUPPORTED,
                            explanation=(
                                "The local demo corpus has no explicit evidence for this criterion."
                            ),
                            evidence_ids=[],
                        )
                    )
        return ComparisonMatrix(
            technology_ids=comparison.technologies,
            criterion_ids=comparison.criteria,
            cells=cells,
            summary="Development-only comparison fixture; not a production corpus result.",
        )
