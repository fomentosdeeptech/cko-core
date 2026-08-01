# CKO Index Operations

Structural operation types are `ADD`, `REMOVE`, `REPLACE`, `REBUILD`, `CLEAR`, and `MERGE`. `IndexBuilder` implements all six in transient memory. `InMemoryIndexOperations` provides generic execution for operations fully described by keys/references and deliberately directs entity-dependent replace/rebuild work to the builder.

Every build returns a new immutable `CanonicalIndex`, increments the structural revision when based on an existing index, retains the prior digest as `parent_digest`, recalculates descriptor counts/digest, and leaves the prior value unchanged. `IndexOperationResult` records operation, previous/resulting versions, affected entry count, warnings, resulting digest, and UTC timestamp. No transaction, Unit of Work, journal, or persistence exists.

`MERGE` requires identical definition IDs and re-applies normal uniqueness/duplicate checks. `REMOVE` rejects a prohibited no-effect operation. `CLEAR` emits a valid empty index. Reference replacement removes the old version and inserts the new reference under the requested key.

`IndexQuery` is a structural read model, not SPR-014 `CanonicalQuery`. It supports an exact key, exact key set, text prefix, inclusive comparable range, reference type, semantic version, namespace, limit, and offset. `InMemoryIndexReader` deterministically orders keys, filters minimal references, deduplicates results, applies pagination, and returns only `IndexReference`, matched keys, counts, source digest, and result metadata. It provides no parser, planner, ranking, scoring, full-text, fuzzy, or semantic behavior.
