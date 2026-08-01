PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cko_schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cko_kb_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_uid TEXT NOT NULL UNIQUE,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    extension TEXT,
    sha256 TEXT,
    size_bytes INTEGER,
    modified_at TEXT,
    discovered_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cko_kb_documents_sha256
ON cko_kb_documents(sha256);

CREATE INDEX IF NOT EXISTS idx_cko_kb_documents_file_path
ON cko_kb_documents(file_path);

CREATE INDEX IF NOT EXISTS idx_cko_kb_documents_status
ON cko_kb_documents(status);

CREATE TABLE IF NOT EXISTS cko_kb_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_uid TEXT NOT NULL UNIQUE,
    entity_type TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    attributes_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cko_kb_entities_type_name
ON cko_kb_entities(entity_type, normalized_name);

CREATE TABLE IF NOT EXISTS cko_kb_document_entities (
    document_id INTEGER NOT NULL,
    entity_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL DEFAULT 'mentions',
    confidence REAL NOT NULL DEFAULT 0.0 CHECK(confidence >= 0.0 AND confidence <= 1.0),
    source TEXT NOT NULL DEFAULT 'system',
    created_at TEXT NOT NULL,
    PRIMARY KEY (document_id, entity_id, relation_type),
    FOREIGN KEY(document_id) REFERENCES cko_kb_documents(id) ON DELETE CASCADE,
    FOREIGN KEY(entity_id) REFERENCES cko_kb_entities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cko_kb_document_entities_entity
ON cko_kb_document_entities(entity_id);

CREATE TABLE IF NOT EXISTS cko_kb_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    aggregate_type TEXT NOT NULL,
    aggregate_uid TEXT,
    payload_json TEXT NOT NULL DEFAULT '{}',
    occurred_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cko_kb_events_aggregate
ON cko_kb_events(aggregate_type, aggregate_uid);

CREATE INDEX IF NOT EXISTS idx_cko_kb_events_occurred_at
ON cko_kb_events(occurred_at);
