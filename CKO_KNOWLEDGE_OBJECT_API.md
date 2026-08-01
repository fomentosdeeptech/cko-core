# CKO Knowledge Object API

## Public namespace

The API is available from both `cko.core.knowledge` and `cko.core`. Constants are `KNOWLEDGE_SCHEMA_VERSION` and `KNOWLEDGE_VERSION`.

Canonical models: `KnowledgeObjectId`, `KnowledgeObjectIdentity`, `KnowledgeMetadata`, `KnowledgeContent`, `KnowledgeVersion`, `KnowledgeRelationship`, `KnowledgeClassification`, `KnowledgeProvenance`, `KnowledgeReference`, `KnowledgeAttribute`, `KnowledgeContext`, `KnowledgeObject`, `KnowledgeCollection`, `KnowledgeSnapshot`, `KnowledgeDescriptor`, `KnowledgeQuery`, and `KnowledgeResult`.

Services: `KnowledgeObjectFactory`, `KnowledgeObjectValidator`, and `DeterministicKnowledgeSerializer`.

Official enums: `KnowledgeType`, `RelationshipType`, `KnowledgeStatus`, `KnowledgeConfidence`, `KnowledgeSourceType`, `KnowledgeCategory`, and `KnowledgeContentKind`.

Errors: `KnowledgeError`, `KnowledgeValidationError`, `KnowledgeSerializationError`, `KnowledgeFactoryError`, `KnowledgeVersionError`, and `KnowledgeRelationshipError`. All derive from the consolidated `CKOError` root.

## Construction contract

Supporting models are constructed as immutable values. A `KnowledgeObject` must be requested from `KnowledgeObjectFactory.create` or reconstructed internally with `from_parts`. Required creation inputs are namespace, origin, knowledge type, metadata, content, and creator. The factory supplies a logical UUID when absent, derives the canonical UUID, creates and hashes the version, builds the aggregate, and runs complete validation.

## Content contract

`KnowledgeContent` supports empty, text, JSON-compatible data, neutral structures, fragments, references, bytes, and derived content. Its vocabulary contains no physical media or document formats.

## Query and result contract

`KnowledgeQuery` is a technology-neutral value object containing exact ID, type, status, domain, tag, limit, and offset criteria. It performs no search and has no storage or index dependency. `KnowledgeResult` is an immutable response envelope.

## Stability

Callers should rely only on names exported through `__all__`. Private factory capabilities and normalization functions are not public API.
