# CKO Knowledge Object Versioning

## Model

`KnowledgeVersion` records a UUID `version_id`, optional parent UUID, semantic version label, UTC creation instant, creator, SHA-256 content hash, lifecycle status, schema version, and optional logical object ID. A version is immutable and belongs to the logical identity, not to a physical file.

`KnowledgeObjectFactory` calculates the content hash from the canonical `KnowledgeContent` envelope. `KnowledgeObjectValidator` recalculates that hash and rejects mismatches. Identity version and version-model label must match, and a supplied version object ID must equal the logical object ID.

## Lineage rules

An initial version has no parent. A successor may identify the predecessor's `version_id` as `parent_version`. A version cannot parent itself. Status uses the official `KnowledgeStatus` enumeration. Supersession may additionally be declared through a `SUPERSEDES` relationship; the relationship is declarative and does not create a graph or mutate either object.

Versions never overwrite prior versions. The immutable models provide lineage representation only. Storage, repositories, conflict resolution, migrations, and retention are outside SPR-010.
