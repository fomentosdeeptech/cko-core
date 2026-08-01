from __future__ import annotations

import sqlite3
from pathlib import Path

from cko.metadata.file_metadata import FileMetadata


SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    extension TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    parent_folder TEXT NOT NULL,
    depth INTEGER NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'inventoried',
    first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_documents_name
ON documents(name);

CREATE INDEX IF NOT EXISTS idx_documents_extension
ON documents(extension);

CREATE INDEX IF NOT EXISTS idx_documents_sha256
ON documents(sha256);

CREATE INDEX IF NOT EXISTS idx_documents_category
ON documents(category);
"""


class KnowledgeBase:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout=5000;")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def upsert(self, item: FileMetadata) -> None:
        sql = """
        INSERT INTO documents (
            path, name, extension, size_bytes, created_at,
            modified_at, mime_type, sha256, parent_folder,
            depth, category, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'inventoried')
        ON CONFLICT(path) DO UPDATE SET
            name = excluded.name,
            extension = excluded.extension,
            size_bytes = excluded.size_bytes,
            created_at = excluded.created_at,
            modified_at = excluded.modified_at,
            mime_type = excluded.mime_type,
            sha256 = excluded.sha256,
            parent_folder = excluded.parent_folder,
            depth = excluded.depth,
            category = excluded.category,
            status = 'inventoried',
            last_seen_at = CURRENT_TIMESTAMP
        """
        with self.connect() as connection:
            connection.execute(
                sql,
                (
                    item.path,
                    item.name,
                    item.extension,
                    item.size_bytes,
                    item.created_at,
                    item.modified_at,
                    item.mime_type,
                    item.sha256,
                    item.parent_folder,
                    item.depth,
                    item.category,
                ),
            )

    def count(self) -> int:
        with self.connect() as connection:
            row = connection.execute("SELECT COUNT(*) FROM documents").fetchone()
            return int(row[0]) if row else 0

    def duplicates(self) -> list[dict[str, object]]:
        sql = """
        SELECT sha256, COUNT(*) AS quantity, SUM(size_bytes) AS total_size
        FROM documents
        GROUP BY sha256
        HAVING COUNT(*) > 1
        ORDER BY quantity DESC, total_size DESC
        """
        with self.connect() as connection:
            rows = connection.execute(sql).fetchall()

        return [
            {"sha256": row[0], "quantity": row[1], "total_size": row[2]}
            for row in rows
        ]

    def category_counts(self) -> list[dict[str, object]]:
        sql = """
        SELECT category, COUNT(*)
        FROM documents
        GROUP BY category
        ORDER BY COUNT(*) DESC
        """
        with self.connect() as connection:
            rows = connection.execute(sql).fetchall()

        return [{"category": row[0], "count": row[1]} for row in rows]
