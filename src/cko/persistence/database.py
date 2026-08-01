from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator


class DatabaseError(RuntimeError):
    pass


class Database:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.path), timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 30000")
        return conn

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        conn = self.connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def integrity_check(self) -> str:
        conn = self.connect()
        try:
            row = conn.execute("PRAGMA integrity_check").fetchone()
            if row is None:
                raise DatabaseError("A verificação de integridade não retornou resultado.")
            return str(row[0])
        finally:
            conn.close()

    def tables(self) -> set[str]:
        conn = self.connect()
        try:
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            return {str(r[0]) for r in rows}
        finally:
            conn.close()

    def indexes(self) -> set[str]:
        conn = self.connect()
        try:
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            ).fetchall()
            return {str(r[0]) for r in rows}
        finally:
            conn.close()
