# CKO Index Model Guide

## Definitions and fields

An `IndexDefinition` declares its namespace/name, `IndexType`, accepted `IndexTarget` values, one or more `IndexField` paths, uniqueness, multiplicity, case behavior, missing/multiple-value policies, status, semantic version, description, and frozen metadata. Policies are declarative. Logical paths allow only simple dotted identifiers rooted in official dimensions; they are not SQL, JSONPath, XPath, or expressions.

## Keys and references

`IndexKey` normalizes text, integer, finite decimal, boolean, UUID, UTC datetime, enum value, SHA-256, null where policy permits, and non-nested simple sequences. Empty sequences, arbitrary objects, NaN, and infinities fail validation. `IndexReference` holds only namespace, canonical identifier, `IndexTarget`, semantic version, entity discriminator, optional SHA-256 checksum, and minimal frozen metadata.

## Entries and indexes

`IndexEntry` joins one key to unique, sorted references and records definition ID, version, status, UTC timestamps, and optional metadata. `CanonicalIndex` joins identity, definition, metadata, version, sorted entries, and a verified `IndexDescriptor`. Unique definitions reject more than one reference per key; every reference target must be declared.

## Collections, statistics, and snapshots

`IndexCollection` validates unique canonical index IDs and non-conflicting namespace/name definitions. `IndexStatistics` reports keys, entries, references, unique references, mean and extrema of cardinality, empty keys, logical collisions, and distributions by entity type and namespace. `IndexSnapshot` captures origin, definition, version, digest, entry count, statistics, UTC time, and snapshot type; validation against the source detects alteration.

## Lifecycle

Create definitions and empty indexes through `IndexFactory`; use `IndexBuilder` for entity ingestion and structural changes; validate the immutable result; optionally calculate statistics, snapshot, serialize, or perform simple `IndexQuery` reads. Canonical aggregates cannot be constructed directly.
