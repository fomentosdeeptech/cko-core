# CKO Knowledge Provenance Statement Foundation — Serialization

`DeterministicProvenanceSerializer` is the sole official serializer. It emits strict UTF-8 without BOM or terminal newline, NFC strings, lexicographically sorted object keys, minimal separators, lowercase UUID/enum/SHA values and closed envelopes.

All 13 discriminators include `model`, `schema_version` and `serialization_version`. Optional values are explicit `null`. Unknown, missing or duplicate fields, duplicate JSON keys, unknown discriminators, future versions and semantically equivalent but noncanonical JSON are rejected.

Statement SHA-256 covers the complete canonical envelope except `digest`. D-01 produces 1.309 bytes and `dda22685f6674a51030a4c4eacbb0f4cf5991a8d6d61435c5fa0e9bbb50efd6d`; the transport envelope is 1.385 bytes.

`to_dict`/`from_dict` preserve structure and semantics. `to_json`/`from_json` additionally require byte-for-byte equality. Every accepted public model preserves equality and hash across round-trip.
