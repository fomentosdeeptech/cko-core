# CKO Knowledge Provenance Statement Foundation — Operations

All operations are stateless, deterministic and side-effect free.

`revise` requires a semantic difference, preserves statement identity/category/subject, increments revision exactly once, creates the complete previous-revision reference and recalculates digest. Individual `with_*` and `without_*` methods reject duplicates or absent members and delegate to the same revision semantics.

`compare` returns ordered changed root paths. `verify_digest` returns bool using constant-time comparison; `require_valid_digest` returns `None` or raises `PD001`.

`validate_chain_in_supplied_set` validates only the finite input set, reports external boundaries and deterministically orders nodes, roots and components. It does not claim global acyclicity.

`project_relationships` is explicit, lossy and nonreversible. It creates entity-to-subject, directed, many-to-one Relationships by the public `RelationshipFactory.from_parts` boundary. Attribution and statements without entities return an empty tuple. No projection mutates Graph, Index, Corpus or any source statement.
