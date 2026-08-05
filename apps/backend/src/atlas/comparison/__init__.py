"""Evidence-backed technology comparison contracts."""

from .events import ComparisonEventOrderError, ComparisonEventWriter
from .retrieval import (
    ComparisonRetrievalBranch,
    ComparisonRetrievalService,
    CorpusComparisonBranchRetriever,
)
from .schemas import (
    ComparisonCell,
    ComparisonCellState,
    ComparisonCriterion,
    ComparisonMatrix,
    ComparisonRequest,
    ComparisonRun,
    ComparisonRunStatus,
)

__all__ = [
    "ComparisonCell",
    "ComparisonCellState",
    "ComparisonCriterion",
    "ComparisonEventOrderError",
    "ComparisonEventWriter",
    "ComparisonMatrix",
    "ComparisonRequest",
    "ComparisonRetrievalBranch",
    "ComparisonRetrievalService",
    "ComparisonRun",
    "ComparisonRunStatus",
    "CorpusComparisonBranchRetriever",
]
