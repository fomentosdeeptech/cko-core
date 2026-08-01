# CKO Knowledge Provenance Statement Foundation — Architecture

## Responsibility

`cko.core.provenance` represents immutable, deterministic and versioned declarations of provenance. It is declarative: references remain opaque and no operation performs I/O, resolution, persistence, networking, execution, trust assessment or verification.

## Structure

The namespace is split into value models (`identity`, `references`, `versioning`, `models`, `results`), closed vocabularies and errors, and four public service boundaries: factory, validator, serializer and operations. Canonical-value types, construction tokens, normalization functions and projection helpers remain private.

The aggregate contains one subject, canonically ordered entities, actors, evidence, predecessors and qualifiers, at most one activity, a logical version, optional declared UTC instant and a SHA-256 digest. Construction is factory-only. All 13 public models are frozen, slotted and keyword-only.

## Identity and integrity

Statement identity is UUIDv5 in namespace `84c43be6-4bb5-52a8-9582-a2e8b04d797c`. Its canonical payload contains business namespace, lineage key, category and the subject token. Target version and target digest do not participate.

The digest is SHA-256 over the canonical statement envelope without its own `digest` field. It establishes structural integrity only.

## Dependencies

The core uses stdlib and `cko.core.exceptions.CKOError`. The peripheral Relationship projection imports only public `cko.core.relationships` symbols. There are no reverse dependencies, private imports, Graph/Query/Index/Corpus/Inventory dependencies or infrastructure calls.

## Compatibility

The change is additive. The prior 610 root exports remain present, and the 36 approved names produce 646 unique resolved exports. `KnowledgeProvenance` remains a distinct unchanged legacy model.
