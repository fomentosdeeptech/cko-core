# CKO Knowledge Object Architecture

## Status and boundary

SPR-010 establishes `cko.core.knowledge` as the canonical, technology-neutral representation layer for knowledge. A Knowledge Object represents a unit of knowledge and never a file, connector, storage resource, database, or document format. The package has no imports from Storage, Runtime, Discovery, Checkpoint, Unit of Work, AI, graph, index, repository, or cache modules.

The implementation is part of CORE SDK 1.0.0 and uses schema `1.0`. It reuses the consolidated `CKOError` hierarchy and exposes its public surface through `cko.core`.

## Aggregate

`KnowledgeObject` is the aggregate root. It consists of canonical identity, metadata, neutral content, version lineage, declarative relationships, and contexts. `KnowledgeObjectFactory` is the exclusive constructor and executes `KnowledgeObjectValidator` before returning an aggregate. The direct aggregate constructor rejects calls without the private factory capability.

Identity separates logical, canonical, and optional external identifiers. Canonical identifiers are deterministic UUIDv5 values derived from namespace and logical UUID. Multiple provenances and references allow multiple origins for one Knowledge Object; one source may independently produce multiple objects.

## Immutability and invariants

Every public model is a frozen, slotted dataclass. Sequences normalize to tuples, mappings normalize recursively to sorted read-only mapping proxies, and nested values reject unsupported mutable types, NaN, and infinities. Every time value is timezone-aware and normalized to UTC.

Validation covers schema versions, discriminators, UUIDs, canonical identity, required fields, UTC instants, confidence ranges, duplicate tags, attributes, references, relationships and collection members, self references, relationship membership, version alignment, and content hashes.

## Package map

- `contracts.py`: schema constants, serializer and validator protocols, canonical primitives.
- `identity.py`: logical and canonical identity.
- `metadata.py`: metadata, attributes, classification, provenance, references.
- `models.py`: content and aggregate transport models.
- `versioning.py`: immutable version lineage.
- `relationships.py`: relationship declarations only; no graph behavior.
- `factory.py`: validated aggregate creation.
- `validator.py`: structural and cross-model validation.
- `serializer.py`: strict deterministic JSON round-trip.
- `errors.py` and `enums.py`: stable errors and official vocabulary.

## Explicit exclusions

The foundation contains no persistence, repository, graph, ontology or taxonomy engine, semantic search or index, reasoning, inference, embedding, LLM, vector database, cache, or physical-format logic.
