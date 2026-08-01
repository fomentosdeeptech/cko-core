# CKO Knowledge Provenance Statement Foundation — Integration

| Foundation | Integration |
|---|---|
| Object | opaque `knowledge_object` reference; `KnowledgeProvenance` unchanged |
| Document | opaque `document` reference; authors/sources are not promoted |
| Relationship | explicit public-API projection through `from_parts` |
| Graph | no import or automatic update |
| Query | not a target and not imported |
| Index | opaque textual reference only; no update |
| Corpus | opaque textual reference only; no authority or membership |
| Inventory | not imported, targeted or extended |

Relationship projection accepts only Knowledge Object and Document endpoints with logical ID, canonical ID, version and declared statement instant. Document endpoints use `canonical_document`. It preserves statement ID/revision/digest/category and entity role in metadata; actors, detailed activity, evidence, predecessors, qualifiers and joint n-ary semantics are intentionally lost.

The public root integration is strictly additive: 610 previous exports plus 36 provenance exports, totaling 646 unique resolved names with zero nominal collisions.
