# CKO Knowledge Index Public API

The stable namespace is `cko.core.index`; its explicit `__all__` publishes 55 unique symbols.

## Construction and services

- `IndexFactory`: `create_definition`, `create_index`, `from_parts`, `create_collection`, `create_snapshot`, and serializer-only snapshot reconstruction.
- `IndexBuilder`: `build`, `from_index`, `add`, `add_reference`, `remove`, `remove_reference`, `replace`, `clear`, `rebuild`, `merge`, `snapshot`, and `statistics`.
- `InMemoryIndexOperations`: structural `ADD`, `REMOVE`, `CLEAR`, and `MERGE` execution with immutable results. Operations needing canonical entities use the builder.
- `InMemoryIndexReader`: structural reads described by `IndexQuery`.
- `DefaultIndexStatisticsProvider`, `DeterministicIndexSerializer`, and `IndexValidator`.

## Models

Identity and structure: `IndexId`, `IndexIdentity`, `IndexMetadata`, `IndexVersion`, `IndexField`, `IndexDefinition`, `IndexDescriptor`.

Content and aggregates: `IndexKey`, `IndexReference`, `IndexEntry`, `CanonicalIndex`, `IndexCollection`, `IndexSnapshot`, `IndexStatistics`.

Operations and reads: `IndexOperation`, `IndexOperationResult`, `IndexQuery`, `IndexResult`.

## Enums

`IndexType`, `IndexTarget`, `IndexStatus`, `IndexOperationType`, `IndexSnapshotType`, `IndexConsistency`, `IndexValuePolicy`, `IndexMultiplicity`, `IndexOrdering`, and `IndexKeyType` use explicit stable string values.

## Contracts and errors

Technology-neutral protocols cover serializer, validator, factory, builder, statistics provider, operation executor, and reader. All index exceptions derive from consolidated `CKOError`: `IndexError`, `IndexValidationError`, `IndexSerializationError`, `IndexFactoryError`, `IndexIdentityError`, `IndexDefinitionError`, `IndexOperationError`, `IndexConsistencyError`, and `IndexQueryError`.

## Root aliases

Because older CORE APIs already expose names with `Index`, `Query`, `Result`, `Statistics`, and `Error`, `cko.core` reexports the new concepts with explicit aliases: `CanonicalIndexType`, `CanonicalIndexQuery`, `CanonicalIndexResult`, `CanonicalIndexStatistics`, and `CanonicalIndexError`. The unambiguous names remain unchanged. This preserves every previous root symbol.
