"""Answer-run persistence port and PostgreSQL implementation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from psycopg import Connection
from psycopg.types.json import Jsonb

from atlas.domain import AnswerDraft, Evidence, Question

AnswerRunState = Literal[
    "accepted",
    "retrieving",
    "composing",
    "verifying",
    "completed",
    "abstained",
    "cancelling",
    "cancelled",
    "failed",
]


class AnswerIdempotencyConflict(RuntimeError):
    """A key is already associated with different question content."""


@dataclass(frozen=True, slots=True)
class AnswerRunRecord:
    id: UUID
    visitor_key_hash: str
    idempotency_key: str
    question: Question
    status: AnswerRunState
    created_at: datetime
    completed_at: datetime | None
    expires_at: datetime


class PostgresAnswerRepository:
    """Store answer state and immutable claim/evidence relationships transactionally."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def create_run(
        self,
        *,
        visitor_key_hash: str,
        idempotency_key: str,
        question: Question,
        expires_at: datetime,
        corpus_snapshot_id: UUID | None = None,
    ) -> AnswerRunRecord:
        row = self._connection.execute(
            """
            SELECT id, question, constraints, status, created_at, completed_at, expires_at
            FROM atlas.answer_runs
            WHERE visitor_key_hash = %s AND idempotency_key = %s
            """,
            (visitor_key_hash, idempotency_key),
        ).fetchone()
        if row is not None:
            existing_question = Question.model_validate(
                {"text": row[1], **(row[2] if isinstance(row[2], dict) else {})}
            )
            if existing_question != question:
                raise AnswerIdempotencyConflict("idempotency key conflicts with another question")
            return AnswerRunRecord(
                id=row[0],
                visitor_key_hash=visitor_key_hash,
                idempotency_key=idempotency_key,
                question=existing_question,
                status=row[3],
                created_at=row[4],
                completed_at=row[5],
                expires_at=row[6],
            )

        constraints = question.model_dump(mode="json")
        constraints.pop("text", None)
        inserted = self._connection.execute(
            """
            INSERT INTO atlas.answer_runs(
              visitor_key_hash, idempotency_key, corpus_snapshot_id, question, constraints,
              status, expires_at
            ) VALUES (%s, %s, %s, %s, %s, 'accepted', %s)
            RETURNING id, created_at
            """,
            (
                visitor_key_hash,
                idempotency_key,
                corpus_snapshot_id,
                question.text,
                Jsonb(constraints),
                expires_at,
            ),
        ).fetchone()
        if inserted is None:
            raise RuntimeError("answer run insert returned no row")
        self._connection.commit()
        return AnswerRunRecord(
            id=inserted[0],
            visitor_key_hash=visitor_key_hash,
            idempotency_key=idempotency_key,
            question=question,
            status="accepted",
            created_at=inserted[1],
            completed_at=None,
            expires_at=expires_at,
        )

    def transition(
        self,
        run_id: UUID,
        status: AnswerRunState,
        *,
        error_code: str | None = None,
    ) -> None:
        terminal = status in {"completed", "abstained", "cancelled", "failed"}
        self._connection.execute(
            """
            UPDATE atlas.answer_runs
            SET status = %s, error_code = %s,
                completed_at = CASE WHEN %s THEN COALESCE(completed_at, now()) ELSE completed_at END
            WHERE id = %s
            """,
            (status, error_code, terminal, run_id),
        )
        self._connection.commit()

    def save_verified_answer(
        self,
        run_id: UUID,
        draft: AnswerDraft,
        evidence: Sequence[Evidence],
    ) -> None:
        evidence_by_id = {item.id: item for item in evidence}
        for claim in draft.claims:
            claim_row = self._connection.execute(
                """
                INSERT INTO atlas.answer_claims(answer_run_id, ordinal, text, claim_type)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (run_id, claim.ordinal, claim.text, claim.type.value),
            ).fetchone()
            if claim_row is None:
                raise RuntimeError("answer claim insert returned no row")
            for evidence_id in claim.citation_ids:
                if evidence_id not in evidence_by_id:
                    raise ValueError("claim references evidence outside the retrieved set")
                self._connection.execute(
                    """
                    INSERT INTO atlas.answer_citations(answer_run_id, claim_id, evidence_id)
                    VALUES (%s, %s, %s)
                    """,
                    (run_id, claim_row[0], evidence_id),
                )
        self._connection.execute(
            """
            UPDATE atlas.answer_runs
            SET answer_status = %s, limitations = %s
            WHERE id = %s
            """,
            (draft.answer_status.value, draft.limitations, run_id),
        )
        self._connection.commit()
