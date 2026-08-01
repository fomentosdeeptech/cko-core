# CKO Knowledge Object Serialization

## Canonical format

`DeterministicKnowledgeSerializer` produces UTF-8 JSON bytes with Unicode preserved, lexicographically sorted object keys, compact separators, and no NaN or infinite numbers. Binary content uses a closed Base64 envelope with `$binary` and `$encoding` keys. Dates use timezone-aware ISO-8601 and are normalized to UTC before serialization.

Every model envelope includes exactly one `schema_version` and one `model` discriminator. Deserialization uses an allowlist of models and an exact field set for each model. Unknown models, unknown or missing fields, unsupported schemas, malformed UUIDs, invalid Base64, invalid UTF-8, and non-canonical JSON are rejected with `KnowledgeSerializationError`.

## Round-trip contract

For every accepted model `x`, `deserialize(serialize(x)) == x`. Deserialization reconstructs deep-frozen mappings, tuples, enums, UUIDs, UTC timestamps, bytes, and nested canonical models. Knowledge Objects are reconstructed through `KnowledgeObjectFactory`, so the round-trip cannot bypass validation.

The serializer rejects semantically valid JSON when its bytes are not the canonical output. This protects deterministic hashing and signatures. `digest(value)` returns lowercase SHA-256 over the exact canonical bytes.

## Compatibility policy

Schema `1.0` is closed. Field additions, removals, discriminator changes, or encoding changes require a new supported schema and an explicit migration policy. This Sprint implements no persistence or migration mechanism.
