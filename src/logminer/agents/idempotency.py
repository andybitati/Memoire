"""Registre persistant d'idempotence pour les effets des tâches Logminer.

La clé d'idempotence appartient au payload de la tâche. Le registre SQLite est
partageable par plusieurs processus locaux ou par plusieurs workers accédant
au même volume. Il ne modifie pas le contrat :class:`AgentMessage`.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class IdempotencyRecord:
    """État persistant associé à une clé d'effet métier."""

    idempotency_key: str
    status: str
    owner: str
    task_id: str
    result: dict[str, Any]
    created_at: str
    updated_at: str


class SQLiteIdempotencyStore:
    """Registre SQLite transactionnel à portée inter-processus."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30.0, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS idempotency_records (
                    idempotency_key TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    result_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _from_row(row: sqlite3.Row | None) -> IdempotencyRecord | None:
        if row is None:
            return None
        try:
            result = json.loads(row["result_json"] or "{}")
        except json.JSONDecodeError:
            result = {"raw": row["result_json"]}
        return IdempotencyRecord(
            idempotency_key=str(row["idempotency_key"]),
            status=str(row["status"]),
            owner=str(row["owner"]),
            task_id=str(row["task_id"]),
            result=result,
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )

    def get(self, idempotency_key: str) -> IdempotencyRecord | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM idempotency_records WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
        return self._from_row(row)

    def reserve(self, idempotency_key: str, *, owner: str, task_id: str) -> tuple[str, IdempotencyRecord | None]:
        """Réserve une clé et retourne `reserved`, `completed` ou `in_progress`."""

        now = _utc_now()
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM idempotency_records WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
            if row is None:
                connection.execute(
                    """
                    INSERT INTO idempotency_records
                    (idempotency_key, status, owner, task_id, result_json, created_at, updated_at)
                    VALUES (?, 'processing', ?, ?, '{}', ?, ?)
                    """,
                    (idempotency_key, owner, task_id, now, now),
                )
                connection.execute("COMMIT")
                return "reserved", None
            connection.execute("COMMIT")
        record = self._from_row(row)
        return ("completed" if record and record.status == "completed" else "in_progress"), record

    def complete(
        self,
        idempotency_key: str,
        *,
        owner: str,
        task_id: str,
        result: dict[str, Any],
    ) -> IdempotencyRecord:
        """Rend le résultat durable avant l'ACK du transport."""

        now = _utc_now()
        serialized = json.dumps(result, ensure_ascii=False, sort_keys=True)
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                INSERT INTO idempotency_records
                (idempotency_key, status, owner, task_id, result_json, created_at, updated_at)
                VALUES (?, 'completed', ?, ?, ?, ?, ?)
                ON CONFLICT(idempotency_key) DO UPDATE SET
                    status = 'completed',
                    owner = excluded.owner,
                    task_id = excluded.task_id,
                    result_json = excluded.result_json,
                    updated_at = excluded.updated_at
                """,
                (idempotency_key, owner, task_id, serialized, now, now),
            )
            connection.execute("COMMIT")
        record = self.get(idempotency_key)
        if record is None:  # pragma: no cover - garde défensive
            raise RuntimeError("Le résultat idempotent n'a pas été persisté")
        return record

    def release_failed(self, idempotency_key: str, *, owner: str) -> bool:
        """Libère une réservation échouée afin qu'une reprise puisse retenter."""

        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                DELETE FROM idempotency_records
                WHERE idempotency_key = ? AND owner = ? AND status = 'processing'
                """,
                (idempotency_key, owner),
            )
        return bool(cursor.rowcount)

    def completed_count(self) -> int:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM idempotency_records WHERE status = 'completed'"
            ).fetchone()
        return int(row["count"] if row else 0)
