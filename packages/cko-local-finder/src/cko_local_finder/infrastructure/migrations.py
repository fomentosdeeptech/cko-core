"""Embedded, checksummed SQLite schema migrations."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import sqlite3

SCHEMA_VERSION = 3
# BEGIN IMMEDIATE serializes adapter writes; the repository updates by this
# logical identity, so schema v1 needs no compatibility-breaking migration.
EXTRACTION_IDENTITY_COLUMNS = ("document_sha256", "extractor", "extractor_version")


class MigrationError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Migration:
    version: int
    name: str
    statements: tuple[str, ...]

    @property
    def checksum(self) -> str:
        logical = "\n".join(statement.strip() for statement in self.statements).encode("utf-8")
        return hashlib.sha256(logical).hexdigest()


MIGRATIONS = (
    Migration(1, "initial_versioned_persistence", (
        """CREATE TABLE schema_migrations (
            version INTEGER PRIMARY KEY, name TEXT NOT NULL, checksum TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )""",
        """CREATE TABLE documents (
            sha256 TEXT PRIMARY KEY, size_bytes INTEGER NOT NULL CHECK(size_bytes >= 0),
            extension TEXT NOT NULL, media_type TEXT NOT NULL,
            physical_metadata_json TEXT NOT NULL, first_seen TEXT NOT NULL, last_seen TEXT NOT NULL
        )""",
        """CREATE TABLE document_locations (
            id INTEGER PRIMARY KEY, document_sha256 TEXT NOT NULL,
            root TEXT NOT NULL, relative_path TEXT NOT NULL,
            observed_size_bytes INTEGER NOT NULL CHECK(observed_size_bytes >= 0),
            mtime_ns INTEGER NOT NULL CHECK(mtime_ns >= 0),
            first_seen TEXT NOT NULL, last_seen TEXT NOT NULL,
            UNIQUE(root, relative_path),
            FOREIGN KEY(document_sha256) REFERENCES documents(sha256)
        )""",
        """CREATE TABLE processing_issues (
            id INTEGER PRIMARY KEY, relative_path TEXT NOT NULL, stage TEXT NOT NULL,
            code TEXT NOT NULL, message TEXT NOT NULL, recoverable INTEGER NOT NULL,
            observed_at TEXT NOT NULL,
            UNIQUE(relative_path, stage, code, message, recoverable)
        )""",
        """CREATE TABLE extractions (
            id INTEGER PRIMARY KEY, document_sha256 TEXT NOT NULL,
            extractor TEXT NOT NULL, extractor_version TEXT NOT NULL,
            status TEXT NOT NULL, text_content TEXT, metadata_json TEXT NOT NULL,
            observed_at TEXT NOT NULL,
            FOREIGN KEY(document_sha256) REFERENCES documents(sha256)
        )""",
        "CREATE INDEX idx_document_locations_document ON document_locations(document_sha256)",
        "CREATE INDEX idx_document_locations_relative_path ON document_locations(relative_path)",
        "CREATE INDEX idx_processing_issues_stage_code ON processing_issues(stage, code)",
    )),
    Migration(2, "fts5_search_projection", (
        """CREATE TABLE search_index_documents (
            id INTEGER PRIMARY KEY, document_sha256 TEXT NOT NULL UNIQUE,
            extraction_id INTEGER NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL,
            extension TEXT NOT NULL, media_type TEXT NOT NULL, root TEXT NOT NULL,
            relative_path TEXT NOT NULL, indexed_at TEXT NOT NULL,
            FOREIGN KEY(document_sha256) REFERENCES documents(sha256),
            FOREIGN KEY(extraction_id) REFERENCES extractions(id)
        )""",
        """CREATE VIRTUAL TABLE search_fts USING fts5(
            title, body, content='search_index_documents', content_rowid='id',
            tokenize='unicode61 remove_diacritics 2'
        )""",
        """CREATE TRIGGER search_index_ai AFTER INSERT ON search_index_documents BEGIN
            INSERT INTO search_fts(rowid,title,body) VALUES(new.id,new.title,new.body);
        END""",
        """CREATE TRIGGER search_index_ad AFTER DELETE ON search_index_documents BEGIN
            INSERT INTO search_fts(search_fts,rowid,title,body) VALUES('delete',old.id,old.title,old.body);
        END""",
        """CREATE TRIGGER search_index_au AFTER UPDATE ON search_index_documents BEGIN
            INSERT INTO search_fts(search_fts,rowid,title,body) VALUES('delete',old.id,old.title,old.body);
            INSERT INTO search_fts(rowid,title,body) VALUES(new.id,new.title,new.body);
        END""",
        "CREATE INDEX idx_search_projection_filters ON search_index_documents(extension,media_type,root,relative_path)",
    )),
    Migration(3, "processing_issue_identity", (
        "ALTER TABLE processing_issues ADD COLUMN document_sha256 TEXT NULL REFERENCES documents(sha256)",
        "ALTER TABLE processing_issues ADD COLUMN root TEXT NULL",
        "CREATE INDEX idx_processing_issues_document ON processing_issues(document_sha256)",
        "CREATE INDEX idx_processing_issues_location ON processing_issues(root,relative_path)",
    )),
)


def apply_migrations(
    connection: sqlite3.Connection,
    migrations: tuple[Migration, ...] = MIGRATIONS,
    *,
    applied_at: str = "schema-v1",
) -> int:
    """Apply ordered migrations atomically and verify every recorded checksum."""
    current = int(connection.execute("PRAGMA user_version").fetchone()[0])
    latest = max((migration.version for migration in migrations), default=0)
    if current > latest:
        raise MigrationError("database schema version is newer than this application")
    connection.execute("BEGIN IMMEDIATE")
    try:
        has_history = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'schema_migrations'"
        ).fetchone()
        recorded = {}
        if has_history:
            recorded = dict(connection.execute("SELECT version, checksum FROM schema_migrations"))
        for migration in sorted(migrations, key=lambda item: item.version):
            if migration.version in recorded:
                if recorded[migration.version] != migration.checksum:
                    raise MigrationError("migration checksum mismatch")
                continue
            for statement in migration.statements:
                connection.execute(statement)
            connection.execute(
                "INSERT INTO schema_migrations(version, name, checksum, applied_at) VALUES (?, ?, ?, ?)",
                (migration.version, migration.name, migration.checksum, applied_at),
            )
            connection.execute(f"PRAGMA user_version = {migration.version}")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    return int(connection.execute("PRAGMA user_version").fetchone()[0])
