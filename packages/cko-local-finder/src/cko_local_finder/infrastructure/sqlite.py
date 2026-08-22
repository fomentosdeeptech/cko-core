"""Standard-library SQLite repository for derived Local Finder state."""

from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path, PurePosixPath
import sqlite3
from typing import Iterator

from cko_local_finder.domain.models import (
    DatabaseCapability, DiscoveryIssue, DiscoveryReport, DuplicateGroup,
    ExtractionIssue, ExtractionResult, IndexingSummary, PersistenceSummary, SearchIndexStatus,
    SearchPage, SearchQuery, StoredDocument, StoredLocation,
    DocumentOrigin, DocumentProvenance, DuplicateEvidence, ExtractionProvenance,
    IndexingProvenance, ProcessingIssueRecord, ProvenanceBundle, ReportMetadata,
    IngestionReport, FailureReport, DuplicateReport,
)
from cko_local_finder.infrastructure.migrations import MIGRATIONS, apply_migrations
from cko_local_finder.infrastructure.search import execute_search


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
                current = int(connection.execute("PRAGMA user_version").fetchone()[0])
                if current in (2, 3):
                    return current
                return apply_migrations(connection, MIGRATIONS[:1])
        except sqlite3.Error as exc:
            raise RepositoryError("database operation failed") from exc

    def apply_search_migrations(self) -> int:
        try:
            with self.connection() as connection:
                current = int(connection.execute("PRAGMA user_version").fetchone()[0])
                if current == 3:
                    return current
                return apply_migrations(connection, MIGRATIONS[:2])
        except sqlite3.Error as exc:
            raise RepositoryError("database operation failed") from exc

    def apply_provenance_migrations(self) -> int:
        with self.connection() as connection:
            return apply_migrations(connection, MIGRATIONS)

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
            if self.record_issue(issue, observed_at, root=report.root):
                issues_recorded += 1
        version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        return PersistenceSummary(documents_inserted, documents_updated, locations_inserted, locations_updated, issues_recorded, version)

    def record_issue(self, issue: DiscoveryIssue, observed_at: str, *, root: str | None = None) -> bool:
        connection = self._connection()
        columns = {row[1] for row in connection.execute("PRAGMA table_info(processing_issues)")}
        if "root" in columns:
            cursor = connection.execute(
                "INSERT INTO processing_issues(relative_path,stage,code,message,recoverable,observed_at,root) VALUES(?,?,?,?,?,?,?) ON CONFLICT(relative_path,stage,code,message,recoverable) DO UPDATE SET observed_at=excluded.observed_at,root=excluded.root",
                (issue.path, issue.stage, issue.code, issue.message, int(issue.recoverable), observed_at, root),
            )
        else:
            cursor = connection.execute(
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
        connection = self._connection()
        columns = {row[1] for row in connection.execute("PRAGMA table_info(processing_issues)")}
        if "document_sha256" in columns:
            location = connection.execute(
                "SELECT root FROM document_locations WHERE document_sha256=? AND relative_path=? ORDER BY root LIMIT 1",
                (issue.source_id, issue.path),
            ).fetchone()
            connection.execute(
                "INSERT INTO processing_issues(relative_path,stage,code,message,recoverable,observed_at,document_sha256,root) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(relative_path,stage,code,message,recoverable) DO UPDATE SET observed_at=excluded.observed_at,document_sha256=excluded.document_sha256,root=excluded.root",
                (issue.path, "extraction", issue.code, issue.message, int(issue.recoverable), observed_at,
                 issue.source_id, location["root"] if location else None),
            )
        else:
            connection.execute(
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

    def _index_document_active(self, document_sha256: str, observed_at: str) -> IndexingSummary:
        connection = self._connection()
        existing = connection.execute(
            "SELECT 1 FROM search_index_documents WHERE document_sha256=?", (document_sha256,)
        ).fetchone()
        row = connection.execute(
            """SELECT e.id extraction_id,e.status,e.text_content,d.extension,d.media_type,
                      l.root,l.relative_path
               FROM documents d
               LEFT JOIN extractions e ON e.document_sha256=d.sha256
               LEFT JOIN document_locations l ON l.document_sha256=d.sha256
               WHERE d.sha256=?
               ORDER BY e.id DESC,l.relative_path COLLATE NOCASE,l.relative_path LIMIT 1""",
            (document_sha256,),
        ).fetchone()
        if row is None or row["status"] != "SUCCESS" or not (row["text_content"] or "").strip():
            removed = connection.execute(
                "DELETE FROM search_index_documents WHERE document_sha256=?", (document_sha256,)
            ).rowcount
            return IndexingSummary(1, 0, 0, int(bool(removed)), 1, 0, 2)
        title = PurePosixPath(row["relative_path"]).stem
        if existing:
            connection.execute(
                """UPDATE search_index_documents SET extraction_id=?,title=?,body=?,extension=?,
                   media_type=?,root=?,relative_path=?,indexed_at=? WHERE document_sha256=?""",
                (row["extraction_id"], title, row["text_content"], row["extension"], row["media_type"],
                 row["root"], row["relative_path"], observed_at, document_sha256),
            )
            return IndexingSummary(1, 0, 1, 0, 0, 0, 2)
        connection.execute(
            """INSERT INTO search_index_documents(document_sha256,extraction_id,title,body,extension,
               media_type,root,relative_path,indexed_at) VALUES(?,?,?,?,?,?,?,?,?)""",
            (document_sha256, row["extraction_id"], title, row["text_content"], row["extension"],
             row["media_type"], row["root"], row["relative_path"], observed_at),
        )
        return IndexingSummary(1, 1, 0, 0, 0, 0, 2)

    def index_document(self, document_sha256: str, observed_at: str) -> IndexingSummary:
        with self.transaction():
            return self._index_document_active(document_sha256, observed_at)

    def remove_from_index(self, document_sha256: str) -> bool:
        with self.transaction():
            return bool(self._connection().execute(
                "DELETE FROM search_index_documents WHERE document_sha256=?", (document_sha256,)
            ).rowcount)

    def rebuild_index(self, observed_at: str) -> IndexingSummary:
        with self.transaction():
            connection = self._connection()
            connection.execute("DELETE FROM search_index_documents")
            digests = [row[0] for row in connection.execute("SELECT sha256 FROM documents ORDER BY sha256")]
            totals = [0] * 6
            for digest in digests:
                item = self._index_document_active(digest, observed_at)
                totals = [a + b for a, b in zip(totals, (item.documents_considered, item.documents_indexed,
                          item.documents_updated, item.documents_removed, item.documents_ignored, item.failures))]
        return IndexingSummary(*totals, 2)

    def search(self, query: SearchQuery) -> SearchPage:
        with self.connection() as connection:
            try:
                return execute_search(connection, query)
            except sqlite3.Error as exc:
                raise RepositoryError("search operation failed") from exc

    def search_index_status(self) -> SearchIndexStatus:
        capability = self.capabilities()
        with self.connection() as connection:
            exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='search_index_documents'"
            ).fetchone()
            count = connection.execute("SELECT count(*) FROM search_index_documents").fetchone()[0] if exists else 0
        return SearchIndexStatus(capability.fts5_available, int(count), capability.schema_version,
                                 capability.schema_version not in (2, 3))

    @staticmethod
    def _issue(row: sqlite3.Row) -> ProcessingIssueRecord:
        return ProcessingIssueRecord(row["document_sha256"], row["root"], row["relative_path"],
                                     row["stage"], row["code"], row["message"],
                                     bool(row["recoverable"]), row["observed_at"])

    def provenance_by_sha256(self, sha256: str) -> ProvenanceBundle | None:
        with self.connection() as connection:
            document = connection.execute("SELECT * FROM documents WHERE sha256=?", (sha256,)).fetchone()
            if document is None:
                return None
            location_rows = connection.execute(
                "SELECT * FROM document_locations WHERE document_sha256=? ORDER BY root,relative_path COLLATE NOCASE,relative_path",
                (sha256,),
            ).fetchall()
            origins = tuple(DocumentOrigin(row["root"], row["relative_path"], row["observed_size_bytes"], row["mtime_ns"])
                            for row in location_rows)
            extraction_row = connection.execute(
                "SELECT * FROM extractions WHERE document_sha256=? ORDER BY id DESC LIMIT 1", (sha256,)
            ).fetchone()
            extraction = None if extraction_row is None else ExtractionProvenance(
                extraction_row["extractor"], extraction_row["extractor_version"],
                extraction_row["status"], extraction_row["observed_at"])
            indexed_row = connection.execute(
                "SELECT indexed_at FROM search_index_documents WHERE document_sha256=?", (sha256,)
            ).fetchone()
            indexing = IndexingProvenance(indexed_row is not None, indexed_row["indexed_at"] if indexed_row else None)
            issues = tuple(self._issue(row) for row in connection.execute(
                "SELECT * FROM processing_issues WHERE document_sha256=? ORDER BY observed_at,stage,code,root,relative_path",
                (sha256,),
            ))
            unresolved = tuple(self._issue(row) for row in connection.execute(
                "SELECT * FROM processing_issues WHERE document_sha256 IS NULL ORDER BY observed_at,stage,code,coalesce(root,''),relative_path"
            ))
        duplicate = DuplicateEvidence(sha256, origins) if len(origins) >= 2 else None
        provenance = DocumentProvenance(sha256, document["size_bytes"], document["extension"],
                                        document["media_type"], origins, extraction, indexing, issues, duplicate)
        return ProvenanceBundle(provenance, unresolved)

    def provenance_by_location(self, root: str, relative_path: str) -> ProvenanceBundle | None:
        relative = PurePosixPath(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("relative_path must remain confined")
        with self.connection() as connection:
            row = connection.execute(
                "SELECT document_sha256 FROM document_locations WHERE root=? AND relative_path=?",
                (root, relative.as_posix()),
            ).fetchone()
        return None if row is None else self.provenance_by_sha256(row["document_sha256"])

    def ingestion_report(self, root: str, observed_at: str) -> IngestionReport:
        with self.connection() as connection:
            locations = connection.execute("SELECT count(*) FROM document_locations WHERE root=?", (root,)).fetchone()[0]
            unique = connection.execute("SELECT count(DISTINCT document_sha256) FROM document_locations WHERE root=?", (root,)).fetchone()[0]
            successful = connection.execute("SELECT count(DISTINCT e.document_sha256) FROM extractions e JOIN document_locations l ON l.document_sha256=e.document_sha256 WHERE l.root=? AND e.status='SUCCESS'", (root,)).fetchone()[0]
            no_text = connection.execute("SELECT count(DISTINCT e.document_sha256) FROM extractions e JOIN document_locations l ON l.document_sha256=e.document_sha256 WHERE l.root=? AND e.status='NO_TEXT'", (root,)).fetchone()[0]
            failures = connection.execute("SELECT count(*) FROM processing_issues WHERE root=? AND recoverable=1", (root,)).fetchone()[0]
            indexed = connection.execute("SELECT count(DISTINCT s.document_sha256) FROM search_index_documents s JOIN document_locations l ON l.document_sha256=s.document_sha256 WHERE l.root=?", (root,)).fetchone()[0]
            duplicate_rows = connection.execute("SELECT count(*) locations FROM document_locations GROUP BY document_sha256 HAVING count(*)>1").fetchall()
        return IngestionReport(ReportMetadata(root, observed_at), locations, unique, unique, 0, successful,
                               no_text, failures, indexed, len(duplicate_rows), sum(row[0] for row in duplicate_rows))

    def failure_report(self, root: str | None, observed_at: str) -> FailureReport:
        with self.connection() as connection:
            resolved_sql = "SELECT * FROM processing_issues WHERE document_sha256 IS NOT NULL"
            params: tuple[object, ...] = ()
            if root is not None:
                resolved_sql += " AND root=?"; params = (root,)
            resolved_sql += " ORDER BY observed_at,stage,code,document_sha256,relative_path"
            resolved = tuple(self._issue(row) for row in connection.execute(resolved_sql, params))
            unresolved = tuple(self._issue(row) for row in connection.execute(
                "SELECT * FROM processing_issues WHERE document_sha256 IS NULL ORDER BY observed_at,stage,code,coalesce(root,''),relative_path"))
        return FailureReport(ReportMetadata(root, observed_at), resolved, unresolved)

    def duplicate_report(self, root: str | None, observed_at: str) -> DuplicateReport:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM document_locations WHERE document_sha256 IN (SELECT document_sha256 FROM document_locations GROUP BY document_sha256 HAVING count(*)>1) ORDER BY document_sha256,root,relative_path COLLATE NOCASE,relative_path"
            ).fetchall()
        groups: dict[str, list[DocumentOrigin]] = {}
        for row in rows:
            if root is None or row["root"] == root:
                groups.setdefault(row["document_sha256"], []).append(DocumentOrigin(
                    row["root"], row["relative_path"], row["observed_size_bytes"], row["mtime_ns"]))
        duplicates = tuple(DuplicateEvidence(digest, tuple(origins)) for digest, origins in sorted(groups.items())
                           if len(origins) >= 2 or root is None)
        return DuplicateReport(ReportMetadata(root, observed_at), duplicates)
