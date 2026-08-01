# CKO Knowledge Provenance Statement Foundation — API

## Constants

`PROVENANCE_SCHEMA_VERSION`, `PROVENANCE_SERIALIZATION_VERSION`, `PROVENANCE_UUID_NAMESPACE`, `PROVENANCE_VERSION`.

## Enums

`ProvenanceStatementCategory`, `ProvenanceTargetType`, `ProvenanceEntityRole`, `ProvenanceActorType`, `ProvenanceActorRole`, `ProvenanceActivityType`, `ProvenanceEvidenceType`.

Values are closed and serialize by their exact lowercase value. In particular, `supporting`, `responsible` and `other` are invalid; the approved values are `supporting_entity`, `responsible_party` and `other_declared`.

## Models

`ProvenanceStatementId`, `ProvenanceStatementIdentity`, `ProvenanceQualifier`, `ProvenanceSubjectRef`, `ProvenanceEntityRef`, `ProvenanceActorRef`, `ProvenanceActivityRef`, `ProvenanceEvidenceRef`, `ProvenanceStatementRef`, `ProvenanceStatementVersion`, `ProvenanceStatement`, `ProvenanceStatementComparisonResult`, `ProvenanceChainValidationResult`.

All are `dataclass(frozen=True, slots=True, kw_only=True)`. `ProvenanceStatement` can only be constructed through `ProvenanceStatementFactory`.

## Services

- `ProvenanceStatementFactory`: `create` and `from_parts`.
- `ProvenanceStatementValidator`: model and supplied-set chain validation.
- `DeterministicProvenanceSerializer`: closed dictionary/JSON envelopes, canonical bytes and digest.
- `ProvenanceOperations`: immutable revision and `with_*`/`without_*` methods, comparison, digest verification, chain validation and explicit Relationship projection.

## Errors

`ProvenanceError`, `ProvenanceValidationError`, `ProvenanceSerializationError`, `ProvenanceFactoryError`, `ProvenanceIdentityError`, `ProvenanceVersionError`, `ProvenanceDigestError`, `ProvenanceChainError`.

Every emitted domain error exposes `code`, `model`, `field`, `detail` and the deterministic message `<code>:<model>:<field>:<detail>`.
