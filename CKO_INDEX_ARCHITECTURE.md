# CKO Knowledge Index Architecture

## Purpose and boundary

`cko.core.index` is the technology-neutral, in-memory organization layer for canonical references. An index is not knowledge, search, a canonical query, a database, persistence, cache, ranking, or an optimization plan. It stores normalized keys, minimal canonical references, structural metadata, versions, statistics, and integrity digests. It never stores a complete indexed entity.

## Structure

The immutable path is `IndexDefinition -> CanonicalIndex -> IndexEntry -> IndexReference`. `IndexFactory` is the mandatory boundary for definitions, indexes, collections, and snapshots. `IndexBuilder` alone owns transient `dict`/`list` state and always emits a frozen `CanonicalIndex`. `InMemoryIndexOperations` applies structural changes; `InMemoryIndexReader` reads exact keys, sets, text prefixes, ordered ranges, and reference metadata. Neither component imports or executes SPR-014 `CanonicalQuery`.

All 18 public models are `@dataclass(frozen=True, slots=True)`. Mappings are recursively converted to read-only mapping proxies and sequences to tuples. Logical paths use a closed dotted-name grammar and an allowlist of dimensions. Canonical ordering is based on key type plus canonical JSON value; references use entity type, namespace, canonical identifier, and version.

## Identity and integrity

`IndexId` distinguishes logical, canonical, definition, index, and snapshot identifiers. Definition IDs derive from normalized structural declarations using UUIDv5. Canonical index IDs derive from namespace, logical ID, definition ID, and semantic version. Entry identities are their canonical keys; referenced-entity identities remain external canonical IDs. No filesystem path or memory address participates in identity.

The index descriptor digest is SHA-256 over the normalized definition ID, version, and deterministically ordered entries. Snapshot IDs derive from origin identity, digest, and snapshot type. `IndexValidator` recomputes index digests and detects content alteration and inconsistent snapshots.

## Integration

The builder accepts the public canonical aggregate types from `cko.core.knowledge`, `documents`, `relationships`, `graph`, and `query`, converts only public identity/metadata fields into `IndexReference`, and rejects targets not declared by the definition. Integration with query is reference-only: no adapter to or execution of `CanonicalQuery` exists.

## Deliberate exclusions

No filesystem, temporary file, SQL/SQLite, persistence, external index/search library, text analysis, fuzzy/full-text/semantic search, embeddings, AI, graph engine, Runtime, Discovery, Checkpoint, Unit of Work, Storage, planner, optimizer, ranking, or scoring is present.
