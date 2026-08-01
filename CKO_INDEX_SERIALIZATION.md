# CKO Index Serialization

`DeterministicIndexSerializer` supports every public serializable index model and enforces strict round-trip equality: `deserialize(serialize(value)) == value`.

Serialization is UTF-8 JSON with preserved Unicode, sorted object keys, canonical separators, and `allow_nan=False`. Each object requires `model` and `schema_version`. A closed discriminator registry and exact field allowlist reject unknown models, fields, schemas, and missing fields. Deserialization also re-encodes parsed input and rejects any non-canonical byte representation, including alternate whitespace or key ordering.

UUIDs and UTC datetimes use canonical textual values. Finite decimals use a tagged `__index_scalar__` envelope so they do not lose decimal semantics. Heterogeneous sequence keys encode their members as nested `IndexKey` objects, preserving UUID, datetime, boolean, integer, decimal, enum-normalized text, and Unicode values. NaN and infinities are rejected during construction and JSON parsing.

SHA-256 digests operate over the exact canonical UTF-8 bytes. The index content digest separately covers the definition identity, version, and sorted entries and is recomputed by validation. Deserialization of protected aggregates routes through `IndexFactory`, preserving the mandatory construction boundary.
