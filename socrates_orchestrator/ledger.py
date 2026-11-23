"""Transactional local workflow records and events for the Linux controller.

One writer holds an advisory process lock for the lifetime of a Ledger. Readers
may open readonly=True concurrently. The controller owns semantic transitions;
the ledger enforces create-only writes, revision comparison, and atomic events.
"""

from __future__ import annotations

from collections.abc import Collection, Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
from typing import Any

try:
    import fcntl
except ImportError:  # Keep package importable; the optional runtime is Linux-only.
    fcntl = None


class LedgerBusy(RuntimeError):
    """Another controller owns the writer lock."""


class RevisionConflict(RuntimeError):
    """The record no longer has the revision expected by its caller."""


@dataclass(frozen=True)
class Record:
    kind: str
    id: str
    revision: int
    phase: str | None
    state: str
    data: dict[str, Any]
    updated_at: str


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


class Ledger:
    """A standard-library SQLite store; use as a context manager.

    put(expected_revision=None) creates a record and fails if it exists.
    Updating requires its exact positive revision. Each successful write and its
    event commit together. No automatic task approval or retry occurs here.
    """

    def __init__(self, path: Path, *, readonly: bool = False):
        self.path = Path(path).absolute()
        self.readonly = readonly
        self._connection: sqlite3.Connection | None = None
        self._lock_fd: int | None = None
        try:
            if readonly:
                self._connection = sqlite3.connect(
                    self.path.as_uri() + "?mode=ro", uri=True, isolation_level=None)
            else:
                if fcntl is None:
                    raise RuntimeError("Ledger writers require POSIX file locks")
                self.path.parent.mkdir(parents=True, exist_ok=True)
                lock_path = self.path.with_name(self.path.name + ".lock")
                self._lock_fd = os.open(
                    lock_path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0),
                    0o600)
                try:
                    fcntl.flock(self._lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as exc:
                    raise LedgerBusy(f"Ledger writer already active: {self.path}") from exc
                self._connection = sqlite3.connect(self.path, isolation_level=None)
            self._db.row_factory = sqlite3.Row
            self._db.execute("PRAGMA foreign_keys=ON")
            version = self._db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1) or (readonly and version != 1):
                raise ValueError(f"Unsupported ledger schema version: {version}")
            if not readonly:
                self._db.execute("PRAGMA journal_mode=WAL")
                self._db.execute("PRAGMA synchronous=FULL")
                self._initialize()
        except BaseException:
            self.close()
            raise

    @property
    def _db(self) -> sqlite3.Connection:
        if self._connection is None:
            raise RuntimeError("Ledger is closed")
        return self._connection

    def __enter__(self) -> Ledger:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        if self._lock_fd is not None:
            os.close(self._lock_fd)  # Closing releases flock, including on crash.
            self._lock_fd = None
        # Do not unlink the lock file: another process may already hold its inode.

    @contextmanager
    def _transaction(self) -> Iterator[None]:
        if self.readonly:
            raise PermissionError("Readonly ledger cannot be modified")
        self._db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self._db.execute("COMMIT")
        except BaseException:
            if self._db.in_transaction:
                self._db.execute("ROLLBACK")
            raise

    def _initialize(self) -> None:
        with self._transaction():
            self._db.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    kind TEXT NOT NULL, id TEXT NOT NULL,
                    revision INTEGER NOT NULL CHECK(revision >= 1),
                    phase TEXT, state TEXT NOT NULL, data TEXT NOT NULL,
                    updated_at TEXT NOT NULL, PRIMARY KEY(kind, id)
                )
            """)
            self._db.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL, kind TEXT, id TEXT, revision INTEGER,
                    timestamp TEXT NOT NULL, payload TEXT NOT NULL
                )
            """)
            self._db.execute("PRAGMA user_version=1")

    @staticmethod
    def _record(row: sqlite3.Row) -> Record:
        return Record(row["kind"], row["id"], row["revision"], row["phase"],
                      row["state"], json.loads(row["data"]), row["updated_at"])

    def get(self, kind: str, id: str) -> Record | None:
        row = self._db.execute(
            "SELECT * FROM records WHERE kind=? AND id=?", (kind, id)).fetchone()
        return self._record(row) if row is not None else None

    def list(self, kind: str | None = None, *, state: str | None = None) -> list[Record]:
        clauses, params = [], []
        if kind is not None:
            clauses.append("kind=?")
            params.append(kind)
        if state is not None:
            clauses.append("state=?")
            params.append(state)
        query = "SELECT * FROM records"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        rows = self._db.execute(query + " ORDER BY kind,id", params).fetchall()
        return [self._record(row) for row in rows]

    def put(self, kind: str, id: str, *, data: dict[str, Any], state: str,
            expected_revision: int | None = None, phase: str | None = None,
            event: str = "record.updated",
            event_data: dict[str, Any] | None = None) -> Record:
        """Create or replace one record and append its event atomically."""
        if any(not isinstance(value, str) or not value for value in (kind, id, state, event)):
            raise ValueError("kind, id, state, and event must be nonempty strings")
        if phase is not None and not isinstance(phase, str):
            raise ValueError("phase must be a string or None")
        if not isinstance(data, dict) or (event_data is not None and not isinstance(event_data, dict)):
            raise ValueError("data and event_data must be JSON objects")
        if expected_revision is not None and (
                type(expected_revision) is not int or expected_revision < 1):
            raise ValueError("expected_revision must be None or a positive integer")
        with self._transaction():
            return self._put(kind, id, data=data, state=state, phase=phase,
                             expected_revision=expected_revision, event=event,
                             event_data=event_data or {})

    def _put(self, kind: str, id: str, *, data: dict[str, Any], state: str,
             expected_revision: int | None, phase: str | None,
             event: str, event_data: dict[str, Any]) -> Record:
        previous = self.get(kind, id)
        actual = previous.revision if previous is not None else None
        if actual != expected_revision:
            raise RevisionConflict(f"{kind}/{id}: expected revision {expected_revision}, got {actual}")
        revision = 1 if actual is None else actual + 1
        encoded_data = _json(data)
        now = _timestamp()
        record = Record(kind, id, revision, phase, state, json.loads(encoded_data), now)
        self._db.execute("""
            INSERT INTO records(kind,id,revision,phase,state,data,updated_at)
            VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(kind,id) DO UPDATE SET revision=excluded.revision,
                phase=excluded.phase, state=excluded.state, data=excluded.data,
                updated_at=excluded.updated_at
        """, (kind, id, revision, phase, state, encoded_data, now))
        self._db.execute("""
            INSERT INTO events(event,kind,id,revision,timestamp,payload)
            VALUES(?,?,?,?,?,?)
        """, (event, kind, id, revision, now, _json({
            "before": asdict(previous) if previous is not None else None,
            "after": asdict(record), "details": event_data,
        })))
        return record

    def append_event(self, event: str, *, data: dict[str, Any]) -> int:
        """Append an audit event without changing a record; return its sequence."""
        if not isinstance(event, str) or not event or not isinstance(data, dict):
            raise ValueError("Supply an event name and a JSON object")
        with self._transaction():
            cursor = self._db.execute(
                "INSERT INTO events(event,timestamp,payload) VALUES(?,?,?)",
                (event, _timestamp(), _json(data)))
            return int(cursor.lastrowid)

    def events(self, after_sequence: int = 0) -> list[dict[str, Any]]:
        if type(after_sequence) is not int or after_sequence < 0:
            raise ValueError("after_sequence must be a nonnegative integer")
        rows = self._db.execute(
            "SELECT * FROM events WHERE sequence>? ORDER BY sequence",
            (after_sequence,)).fetchall()
        return [dict(row, payload=json.loads(row["payload"])) for row in rows]

    def recover_interrupted(
        self, *, kinds: Collection[str] = ("invocation",),
        active_states: Collection[str] = ("running",),
        reason: str = "controller restarted",
    ) -> list[Record]:
        """Explicitly mark abandoned records interrupted in one transaction.

        A released controller lock does not prove its child agents stopped. The
        caller must reconcile process/worktree ownership before launching a retry.
        This operation records uncertainty; it never resumes or approves work.
        """
        if not isinstance(reason, str) or not reason:
            raise ValueError("A recovery reason is required")
        recovered = []
        with self._transaction():
            for record in self.list():
                if record.kind not in kinds or record.state not in active_states:
                    continue
                data = dict(record.data, recovery_reason=reason,
                            interrupted_from_state=record.state)
                recovered.append(self._put(
                    record.kind, record.id, data=data, state="interrupted",
                    phase=record.phase, expected_revision=record.revision,
                    event="record.interrupted", event_data={"reason": reason}))
        return recovered
