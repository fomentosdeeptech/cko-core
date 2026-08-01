PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    sha256 TEXT NOT NULL UNIQUE,
    filename TEXT NOT NULL,
    extension TEXT,
    mime_type TEXT,
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    created_at TEXT,
    modified_at TEXT,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS locations (
    location_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    full_path TEXT NOT NULL UNIQUE,
    exists_flag INTEGER NOT NULL DEFAULT 1 CHECK (exists_flag IN (0, 1)),
    observed_at TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

CREATE INDEX IF NOT EXISTS idx_documents_sha256
ON documents(sha256);

CREATE INDEX IF NOT EXISTS idx_locations_document_id
ON locations(document_id);

CREATE INDEX IF NOT EXISTS idx_locations_full_path
ON locations(full_path);
