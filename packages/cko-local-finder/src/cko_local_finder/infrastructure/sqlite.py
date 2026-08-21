"""Standard-library SQLite repository for derived Local Finder state."""

from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
from typing import Iterator

from cko_local_finder.domain.models import (
    DatabaseCapability, DiscoveryIssue, DiscoveryReport, DuplicateGroup,
    ExtractionIssue, ExtractionResult, PersistenceSummary, StoredDocument, StoredLocation,
)
from cko_local_finder.infrastructure.migrations import apply_migrations


class RepositoryError(RuntimeError):
    pass


def _probe_fts5(connection: sqlite3.Connection) -> bool:
    try:
        connection.execute("CREATE VIRTUAL TABLE temp.fts5_capability_probe USING fts5(value)")
        connection.execute("INSERT INTO fts5_capability_probe(value) VALUES (?)", ("probe",))
        return connection.execute("SELECT count(*) FROM fts5_capability_probe").fetchone()[0] == 1
    except sqlite3.Error:
        return False
    finally:
        connection.execute("DROP TABLE IF EXISTS temp.fts5_capability_probe")


class SQLiteDocumentRepository:
    def __init__(self, database_path: str | Path, *, busy_timeout_ms: int = 5000) -> None:
        if not isinstance(database_path, (str, Path)) or not str(database_path).strip():
            raise ValueError("database_path must be explicit")
        if busy_timeout_ms <= 0:
            raise ValueError("busy_timeout_ms must be positive")
        self.database_path = str(database_path)
        self.busy_timeout_ms = busy_timeout_ms
        if self.database_path != ":memory:":
            path = Path(database_path)
            if not path.parent.exists():
                raise ValueError("database parent directory must already exist")
            self.database_path = str(path)
        self._active: sqlite3.Connection | None = None

    def _open(self) -> sqlite3.Connection:
        try:
            connection = sqlite3.connect(self.database_path, isolation_level=None)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms}")
            return connection
        except sqlite3.Error as exc:
            raise RepositoryError("database could not be opened") from exc

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._open()
        try:
            yield connection
        finally:
            connection.close()

    def apply_migrations(self) -> int:
        try:
            with self.connection() as connection:
                return apply_migrations(connection)
        except sqlite3.Error as exc:
            raise RepositoryError("database operation failed") from exc

    @contextmanager
    def transaction(self) -> Iterator[None]:
        if self._active is not None:
            raise RepositoryError("nested transactions are not supported")
        connection = self._open()
        self._active = connection
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            self._active = None
            connection.close()

    def _connection(self) -> sqlite3.Connection:
        if self._active is None:
            raise RepositoryError("operation requires an active transaction")
        return self._active

    def persist_report(self, report: DiscoveryReport, observed_at: str) -> PersistenceSummary:
        connection = self._connection()
        documents_inserted = documents_updated = locations_inserted = locations_updated = issues_recorded = 0
        for item in report.files:
            exists = connection.execute("SELECT 1 FROM documents WHERE sha256 = ?", (item.sha256,)).fetchone()
            metadata = json.dumps({"hidden": item.hidden}, sort_keys=True, separators=(",", ":"))
            if exists:
                connection.execute(
                    "UPDATE documents SET size_bytes=?, extension=?, media_type=?, physical_metadata_json=?, last_seen=? WHERE sha256=?",
                    (item.size_bytes, item.extension, item.media_type, metadata, observed_at, item.sha256),
                )
                documents_updated += 1
            else:
                connection.execute(
                    "INSERT INTO documents(sha256,size_bytes,extension,media_type,physical_metadata_json,first_seen,last_seen) VALUES(?,?,?,?,?,?,?)",
                    (item.sha256, item.size_bytes, item.extension, item.media_type, metadata, observed_at, observed_at),
                )
                documents_inserted += 1
            location = connection.execute(
                "SELECT id FROM document_locations WHERE root=? AND relative_path=?", (report.root, item.relative_path)
            ).fetchone()
            if location:
                connection.execute(
                    "UPDATE document_locations SET document_sha256=?,observed_size_bytes=?,mtime_ns=?,last_seen=? WHERE id=?",
                    (item.sha256, item.size_bytes, item.modified_at_ns, observed_at, location["id"]),
                )
                locations_updated += 1
            else:
                connection.execute(
                    "INSERT INTO document_locations(document_sha256,root,relative_path,observed_size_bytes,mtime_ns,first_seen,last_seen) VALUES(?,?,?,?,?,?,?)",
                    (item.sha256, report.root, item.relative_path, item.size_bytes, item.modified_at_ns, observed_at, observed_at),
                )
                locations_inserted += 1
        for issue in report.issues:
            if self.record_issue(issue, observed_at):
                issues_recorded += 1
        version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        return PersistenceSummary(documents_inserted, documents_updated, locations_inserted, locations_updated, issues_recorded, version)

    def record_issue(self, issue: DiscoveryIssue, observed_at: str) -> bool:
        cursor = self._connection().execute(
            "INSERT INTO processing_issues(relative_path,stage,code,message,recoverable,observed_at) VALUES(?,?,?,?,?,?) ON CONFLICT(relative_path,stage,code,message,recoverable) DO UPDATE SET observed_at=excluded.observed_at",
            (issue.path, issue.stage, issue.code, issue.message, int(issue.recoverable), observed_at),
        )
        return cursor.rowcount == 1

    def save_extraction(self, result: ExtractionResult, observed_at: str) -> None:
        connection = self._connection()
        metadata = json.dumps(dict(result.metadata), sort_keys=True, separators=(",", ":"))
        existing = connection.execute(
            "SELECT id FROM extractions WHERE document_sha256=? AND extractor=? AND extractor_version=? ORDER BY id LIMIT 1",
            (result.source_id, result.extractor, result.extractor_version),
        ).fetchone()
        if existing:
            connection.execute(
                "UPDATE extractions SET status=?,text_content=?,metadata_json=?,observed_at=? WHERE id=?",
                (result.status, result.text, metadata, observed_at, existing["id"]),
            )
        else:
            connection.execute(
                "INSERT INTO extractions(document_sha256,extractor,extractor_version,status,text_content,metadata_json,observed_at) VALUES(?,?,?,?,?,?,?)",
                (result.source_id, result.extractor, result.extractor_version, result.status,
                 result.text, metadata, observed_at),
            )

    def get_extraction(self, document_sha256: str, extractor: str,
                       extractor_version: str) -> ExtractionResult | None:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT * FROM extractions WHERE document_sha256=? AND extractor=? AND extractor_version=? ORDER BY id DESC LIMIT 1",
                (document_sha256, extractor, extractor_version),
            ).fetchone()
        if row is None:
            return None
        metadata = tuple(sorted((str(key), str(value)) for key, value in json.loads(row["metadata_json"]).items()))
        return ExtractionResult(row["document_sha256"], row["text_content"] or "", row["extractor"],
                                row["extractor_version"], metadata, row["status"])

    def record_extraction_issue(self, issue: ExtractionIssue, observed_at: str) -> None:
        self._connection().execute(
            "INSERT INTO processing_issues(relative_path,stage,code,message,recoverable,observed_at) VALUES(?,?,?,?,?,?) ON CONFLICT(relative_path,stage,code,message,recoverable) DO UPDATE SET observed_at=excluded.observed_at",
            (issue.path, "extraction", issue.code, issue.message, int(issue.recoverable), observed_at),
        )

    def get_document(self, sha256: str) -> StoredDocument | None:
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM documents WHERE sha256=?", (sha256,)).fetchone()
        if row is None:
            return None
        metadata = tuple(sorted((str(key), str(value).lower() if isinstance(value, bool) else str(value)) for key, value in json.loads(row["physical_metadata_json"]).items()))
        return StoredDocument(row["sha256"], row["size_bytes"], row["extension"], row["media_type"], row["first_seen"], row["last_seen"], metadata)

    def list_locations(self, sha256: str) -> tuple[StoredLocation, ...]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM document_locations WHERE document_sha256=? ORDER BY relative_path COLLATE NOCASE, relative_path",
                (sha256,),
            ).fetchall()
        return tuple(StoredLocation(row["document_sha256"], row["root"], row["relative_path"], row["observed_size_bytes"], row["mtime_ns"], row["first_seen"], row["last_seen"]) for row in rows)

    def find_duplicates(self) -> tuple[DuplicateGroup, ...]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT d.sha256,d.size_bytes,l.relative_path FROM documents d JOIN document_locations l ON l.document_sha256=d.sha256 WHERE d.sha256 IN (SELECT document_sha256 FROM document_locations GROUP BY document_sha256 HAVING count(*) >= 2) ORDER BY d.sha256,l.relative_path COLLATE NOCASE,l.relative_path"
            ).fetchall()
        grouped: dict[str, list[str]] = {}
        sizes: dict[str, int] = {}
        for row in rows:
            grouped.setdefault(row["sha256"], []).append(row["relative_path"])
            sizes[row["sha256"]] = row["size_bytes"]
        return tuple(DuplicateGroup(digest, sizes[digest], tuple(paths)) for digest, paths in sorted(grouped.items()))

    def capabilities(self) -> DatabaseCapability:
        with self.connection() as connection:
            foreign_keys = bool(connection.execute("PRAGMA foreign_keys").fetchone()[0])
            schema_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            available = _probe_fts5(connection)
        return DatabaseCapability(sqlite3.sqlite_version, available, foreign_keys, schema_version)
