"""Agent package with lazy compatibility exports.

Provider ports import the tool schemas at runtime.  Importing the cited-answer graph eagerly from
this package initializer would then import those same provider ports again and create a circular
dependency.  Keep the historical package-level exports lazy while internal code imports concrete
modules directly.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from atlas.agent.cited_answer_graph import CitedAnswerDependencies, CitedAnswerGraph

__all__ = ["CitedAnswerDependencies", "CitedAnswerGraph"]


def __getattr__(name: str) -> object:
    if name in __all__:
        from atlas.agent.cited_answer_graph import CitedAnswerDependencies, CitedAnswerGraph

        return {
            "CitedAnswerDependencies": CitedAnswerDependencies,
            "CitedAnswerGraph": CitedAnswerGraph,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
