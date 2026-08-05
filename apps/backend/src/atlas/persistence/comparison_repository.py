"""Persistence ports for comparison lifecycle and verified matrices."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from threading import RLock
from typing import Protocol
from uuid import UUID

from psycopg import Connection

from atlas.comparison.schemas import (
    ComparisonCell,
    ComparisonCellState,
    ComparisonCriterion,
    ComparisonMatrix,
    ComparisonRun,
    ComparisonRunStatus,
)
from atlas.domain import CollectionSlug


class ComparisonRunNotFound(KeyError):
    """The run does not exist or belongs to another anonymous visitor."""


@dataclass(frozen=True, slots=True)
class StoredComparison:
    run: ComparisonRun
    matrix: ComparisonMatrix | None = None


class ComparisonRepository(Protocol):
    def create(self, run: ComparisonRun, *, idempotency_key: str | None = None) -> None: ...

    def get(self, run_id: UUID, *, visitor_key_hash: str) -> StoredComparison: ...

    def save_matrix(self, run_id: UUID, matrix: ComparisonMatrix) -> None: ...

    def complete(
        self,
        run_id: UUID,
        *,
        visitor_key_hash: str,
        completed_at: datetime,
    ) -> ComparisonRun: ...


class InMemoryComparisonRepository:
    """Small deterministic repository used by workflow tests and local development."""

    def __init__(self) -> None:
        self._records: dict[UUID, StoredComparison] = {}
        self._lock = RLock()

    def create(self, run: ComparisonRun, *, idempotency_key: str | None = None) -> None:
        del idempotency_key
        with self._lock:
            if run.run_id in self._records:
                raise ValueError("comparison run already exists")
            self._records[run.run_id] = StoredComparison(run=run)

    def get(self, run_id: UUID, *, visitor_key_hash: str) -> StoredComparison:
        with self._lock:
            record = self._records.get(run_id)
            if record is None or record.run.visitor_key_hash != visitor_key_hash:
                raise ComparisonRunNotFound(run_id)
            return record

    def save_matrix(self, run_id: UUID, matrix: ComparisonMatrix) -> None:
        with self._lock:
            record = self._records.get(run_id)
            if record is None:
                raise ComparisonRunNotFound(run_id)
            self._records[run_id] = StoredComparison(run=record.run, matrix=matrix)

    def complete(
        self,
        run_id: UUID,
        *,
        visitor_key_hash: str,
        completed_at: datetime,
    ) -> ComparisonRun:
        with self._lock:
            record = self.get(run_id, visitor_key_hash=visitor_key_hash)
            if record.matrix is None:
                raise ValueError("comparison cannot complete without a matrix")
            completed = record.run.model_copy(
                update={
                    "status": ComparisonRunStatus.COMPLETED,
                    "completed_at": completed_at,
                }
            )
            self._records[run_id] = StoredComparison(run=completed, matrix=record.matrix)
            return completed


class PostgresComparisonRepository:
    """Persist comparison runs, matrices, cells and corpus evidence links."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def create(self, run: ComparisonRun, *, idempotency_key: str | None = None) -> None:
        key = idempotency_key or str(run.run_id)
        self._connection.execute(
            """
            INSERT INTO atlas.comparison_runs(
              id, request_id, visitor_key_hash, idempotency_key, corpus_snapshot_id,
              status, created_at, completed_at, retained_until
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                run.run_id,
                run.request_id,
                run.visitor_key_hash,
                key,
                run.snapshot_id,
                run.status.value,
                run.created_at,
                run.completed_at,
                run.retained_until,
            ),
        )
        self._connection.commit()

    def get(self, run_id: UUID, *, visitor_key_hash: str) -> StoredComparison:
        run_row = self._connection.execute(
            """
            SELECT id, request_id, visitor_key_hash, corpus_snapshot_id, status,
                   created_at, completed_at, retained_until
            FROM atlas.comparison_runs
            WHERE id = %s AND visitor_key_hash = %s
            """,
            (run_id, visitor_key_hash),
        ).fetchone()
        if run_row is None:
            raise ComparisonRunNotFound(run_id)
        run = ComparisonRun(
            run_id=run_row[0],
            request_id=run_row[1],
            visitor_key_hash=run_row[2].strip(),
            snapshot_id=run_row[3],
            status=ComparisonRunStatus(run_row[4]),
            created_at=run_row[5],
            completed_at=run_row[6],
            retained_until=run_row[7],
        )
        matrix_row = self._connection.execute(
            """
            SELECT id, technology_ids, criterion_ids, summary
            FROM atlas.comparison_matrices
            WHERE comparison_run_id = %s
            """,
            (run_id,),
        ).fetchone()
        if matrix_row is None:
            return StoredComparison(run=run)
        cell_rows = self._connection.execute(
            """
            SELECT id, technology_id, criterion_id, state, value, unit, explanation, observed_at
            FROM atlas.comparison_cells
            WHERE comparison_matrix_id = %s
            ORDER BY id
            """,
            (matrix_row[0],),
        ).fetchall()
        cells = []
        for cell_row in cell_rows:
            evidence_rows = self._connection.execute(
                """
                SELECT chunk_id
                FROM atlas.comparison_cell_evidence
                WHERE comparison_cell_id = %s
                ORDER BY ordinal
                """,
                (cell_row[0],),
            ).fetchall()
            cells.append(
                ComparisonCell(
                    technology_id=CollectionSlug(cell_row[1]),
                    criterion_id=ComparisonCriterion(cell_row[2]),
                    state=ComparisonCellState(cell_row[3]),
                    value=cell_row[4],
                    unit=cell_row[5],
                    explanation=cell_row[6],
                    evidence_ids=[row[0] for row in evidence_rows],
                    observed_at=cell_row[7],
                )
            )
        matrix = ComparisonMatrix(
            technology_ids=[CollectionSlug(value) for value in matrix_row[1]],
            criterion_ids=[ComparisonCriterion(value) for value in matrix_row[2]],
            cells=cells,
            summary=matrix_row[3],
        )
        return StoredComparison(run=run, matrix=matrix)

    def save_matrix(self, run_id: UUID, matrix: ComparisonMatrix) -> None:
        matrix_id = UUID(int=0)
        row = self._connection.execute(
            """
            INSERT INTO atlas.comparison_matrices(
              comparison_run_id, technology_ids, criterion_ids, summary
            ) VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (
                run_id,
                [value.value for value in matrix.technology_ids],
                [value.value for value in matrix.criterion_ids],
                matrix.summary,
            ),
        ).fetchone()
        if row is None:
            raise RuntimeError("comparison matrix insert returned no ID")
        matrix_id = row[0]
        for cell in matrix.cells:
            cell_row = self._connection.execute(
                """
                INSERT INTO atlas.comparison_cells(
                  comparison_matrix_id, technology_id, criterion_id, state,
                  value, unit, explanation, observed_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    matrix_id,
                    cell.technology_id.value,
                    cell.criterion_id.value,
                    cell.state.value,
                    cell.value,
                    cell.unit,
                    cell.explanation,
                    cell.observed_at,
                ),
            ).fetchone()
            if cell_row is None:
                raise RuntimeError("comparison cell insert returned no ID")
            for ordinal, evidence_id in enumerate(cell.evidence_ids, start=1):
                self._connection.execute(
                    """
                    INSERT INTO atlas.comparison_cell_evidence(
                      comparison_cell_id, chunk_id, ordinal
                    ) VALUES (%s, %s, %s)
                    """,
                    (cell_row[0], evidence_id, ordinal),
                )
        self._connection.commit()

    def complete(
        self,
        run_id: UUID,
        *,
        visitor_key_hash: str,
        completed_at: datetime,
    ) -> ComparisonRun:
        stored = self.get(run_id, visitor_key_hash=visitor_key_hash)
        if stored.matrix is None:
            raise ValueError("comparison cannot complete without a matrix")
        row = self._connection.execute(
            """
            UPDATE atlas.comparison_runs
            SET status = 'completed', completed_at = %s
            WHERE id = %s AND visitor_key_hash = %s
            RETURNING id, request_id, visitor_key_hash, corpus_snapshot_id, status,
                      created_at, completed_at, retained_until
            """,
            (completed_at, run_id, visitor_key_hash),
        ).fetchone()
        if row is None:
            raise ComparisonRunNotFound(run_id)
        self._connection.commit()
        return ComparisonRun(
            run_id=row[0],
            request_id=row[1],
            visitor_key_hash=row[2].strip(),
            snapshot_id=row[3],
            status=ComparisonRunStatus(row[4]),
            created_at=row[5],
            completed_at=row[6],
            retained_until=row[7],
        )
