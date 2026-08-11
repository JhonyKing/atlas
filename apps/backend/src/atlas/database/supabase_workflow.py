"""Provider-neutral helpers for a safe, repeatable Supabase migration workflow.

The hosted Supabase MCP is the transport.  This module deliberately contains only
deterministic planning and evidence logic so it can be exercised without network
access, credentials, or a live database in unit tests and CI.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from time import perf_counter
from typing import Literal

from atlas.database.environment_gate import EnvironmentGate
from atlas.database.migration_evidence import (
    PROJECT_REF,
    DriftFinding,
    MigrationCheck,
    MigrationEvidence,
)

WorkflowStatus = Literal["passed", "failed", "blocked", "drift_detected"]


class WorkflowError(RuntimeError):
    """Raised when a remote snapshot cannot be safely reconciled."""


@dataclass(frozen=True)
class RemoteSnapshot:
    """Bounded, non-secret state returned by the Supabase MCP."""

    project_ref: str
    environment: str
    remote_revisions: tuple[str, ...]
    tables: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    functions: tuple[str, ...] = ()
    indexes: tuple[str, ...] = ()
    policies: tuple[str, ...] = ()
    extensions: tuple[str, ...] = ()
    seed_identifiers: tuple[str, ...] = ()
    contains_existing_data: bool = False

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> RemoteSnapshot:
        """Build a snapshot from MCP JSON while keeping only bounded identifiers."""

        def strings(name: str) -> tuple[str, ...]:
            raw = payload.get(name, ())
            if not isinstance(raw, (list, tuple)):
                raise WorkflowError(f"remote snapshot field {name!r} must be a list")
            values = tuple(item for item in raw if isinstance(item, str) and item)
            if len(values) != len(raw):
                raise WorkflowError(f"remote snapshot field {name!r} contains non-string values")
            return values

        project_ref = payload.get("project_ref")
        environment = payload.get("environment", "unknown")
        contains_existing_data = payload.get("contains_existing_data", False)
        if not isinstance(project_ref, str) or not isinstance(environment, str):
            raise WorkflowError("remote snapshot requires string project_ref and environment")
        if not isinstance(contains_existing_data, bool):
            raise WorkflowError("contains_existing_data must be boolean")
        return cls(
            project_ref=project_ref,
            environment=environment,
            remote_revisions=strings("remote_revisions"),
            tables=strings("tables"),
            constraints=strings("constraints"),
            functions=strings("functions"),
            indexes=strings("indexes"),
            policies=strings("policies"),
            extensions=strings("extensions"),
            seed_identifiers=strings("seed_identifiers"),
            contains_existing_data=contains_existing_data,
        )

    def inventory(self) -> dict[str, object]:
        """Return an evidence-safe inventory, never row payloads."""

        return {
            "tables": list(self.tables),
            "constraints": list(self.constraints),
            "functions": list(self.functions),
            "indexes": list(self.indexes),
            "policies": list(self.policies),
            "extensions": list(self.extensions),
            "seed_identifiers": list(self.seed_identifiers),
        }


def compare_state(
    repository_revisions: Sequence[str],
    remote: RemoteSnapshot,
    *,
    expected_inventory: Mapping[str, Sequence[str]] | None = None,
) -> list[DriftFinding]:
    """Classify exact revision and object drift without reading row contents."""

    findings: list[DriftFinding] = []
    expected_revisions = tuple(repository_revisions)
    actual_revisions = remote.remote_revisions
    if expected_revisions != actual_revisions:
        common = min(len(expected_revisions), len(actual_revisions))
        for index in range(common):
            if expected_revisions[index] != actual_revisions[index]:
                findings.append(
                    DriftFinding(
                        kind="revision",
                        object_name=f"position-{index + 1}",
                        expected=expected_revisions[index],
                        actual=actual_revisions[index],
                        severity="blocking",
                        resolution="Review the first divergent migration before applying writes.",
                    )
                )
                break
        if len(expected_revisions) != len(actual_revisions):
            findings.append(
                DriftFinding(
                    kind="revision",
                    object_name="history-length",
                    expected=str(len(expected_revisions)),
                    actual=str(len(actual_revisions)),
                    severity="blocking",
                    resolution=(
                        "Reconcile the remote migration history with the repository manifest."
                    ),
                )
            )

    if expected_inventory is not None:
        actual_by_kind: dict[str, Sequence[str]] = {
            "table": remote.tables,
            "function": remote.functions,
            "index": remote.indexes,
            "policy": remote.policies,
            "extension": remote.extensions,
            "seed": remote.seed_identifiers,
        }
        for kind, expected_values in expected_inventory.items():
            actual_values = set(actual_by_kind.get(kind, ()))
            for value in expected_values:
                if value not in actual_values:
                    findings.append(
                        DriftFinding(
                            kind=kind,
                            object_name=value,
                            expected="present",
                            actual="missing",
                            severity="blocking",
                            resolution=(
                                "Apply a reviewed migration or update the repository contract."
                            ),
                        )
                    )
    return findings


def plan_missing_revisions(
    repository_revisions: Sequence[str], remote_revisions: Sequence[str]
) -> tuple[str, ...]:
    """Return only an ordered suffix that can safely be applied."""

    repo = tuple(repository_revisions)
    remote = tuple(remote_revisions)
    if len(remote) > len(repo) or repo[: len(remote)] != remote:
        raise WorkflowError("remote migration history is not an ordered repository prefix")
    return repo[len(remote) :]


@dataclass(frozen=True)
class ApplyResult:
    """Outcome of applying an ordered list through an injected MCP callback."""

    applied: tuple[str, ...]
    failed_revision: str | None
    error: str | None

    @property
    def status(self) -> WorkflowStatus:
        return "failed" if self.failed_revision is not None else "passed"


def apply_ordered(revisions: Sequence[str], apply_revision: Callable[[str], None]) -> ApplyResult:
    """Apply revisions in order and stop immediately at the first failure."""

    applied: list[str] = []
    for revision in revisions:
        try:
            apply_revision(revision)
        except Exception as exc:
            return ApplyResult(tuple(applied), revision, str(exc)[:500])
        applied.append(revision)
    return ApplyResult(tuple(applied), None, None)


def build_evidence(
    *,
    run_id: str,
    mode: Literal["inspect", "apply", "verify"],
    repository_head: str,
    repository_revisions: Sequence[str],
    remote: RemoteSnapshot,
    checks: Sequence[MigrationCheck],
    drift: Sequence[DriftFinding] = (),
    applied_revisions: Sequence[str] = (),
    started_at: str,
    finished_at: str,
    status: WorkflowStatus,
) -> MigrationEvidence:
    """Construct the common evidence artifact from bounded workflow results."""

    return MigrationEvidence.model_validate(
        {
            "run_id": run_id,
            "project_ref": remote.project_ref,
            "environment": remote.environment,
            "mode": mode,
            "started_at": started_at,
            "finished_at": finished_at,
            "repository_head": repository_head,
            "repository_revisions": list(repository_revisions),
            "remote_revisions": list(remote.remote_revisions),
            "applied_revisions": list(applied_revisions),
            "schema_inventory": remote.inventory(),
            "checks": list(checks),
            "drift": list(drift),
            "status": status,
        }
    )


def timed_check(name: str, operation: Callable[[], str]) -> MigrationCheck:
    """Run a bounded local/MCP operation and convert it into a check record."""

    started = perf_counter()
    try:
        detail = operation()
    except Exception as exc:
        return MigrationCheck(
            name=name,
            status="failed",
            elapsed_ms=(perf_counter() - started) * 1000,
            detail=str(exc)[:1000],
        )
    return MigrationCheck(
        name=name,
        status="passed",
        elapsed_ms=(perf_counter() - started) * 1000,
        detail=detail[:1000],
    )


def assert_safe_write(remote: RemoteSnapshot, *, owner_confirmed: bool) -> None:
    """Apply the fail-closed environment gate before any remote write."""

    EnvironmentGate(
        project_ref=remote.project_ref,
        environment=remote.environment,  # type: ignore[arg-type]
        contains_existing_data=remote.contains_existing_data,
        owner_confirmed=owner_confirmed,
    ).assert_write_allowed()
    if remote.project_ref != PROJECT_REF:
        raise WorkflowError(f"expected Supabase project {PROJECT_REF}")
