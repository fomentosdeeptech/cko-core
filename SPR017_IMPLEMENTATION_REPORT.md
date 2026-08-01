# SPR-017 — Implementation Report

## 1. Identification and baseline

- Repository: `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`.
- Initial branch: `main`.
- Initial commit: `e94545919db97a071f08de2c08ce1a5dde06980e`.
- Specification SHA-256: `D19FA36A85F9BB761A11E65EC32D4D39A9C8BB8DFD290F621101488DB0B4862D`.
- Final-verification report SHA-256: `93D50E88848DC6FC98B53670A381D45D5B52068DC490B3544B1DCFCB8CBE05BB`.
- Specification format: 128.960 bytes, 1.358 content lines, UTF-8 without BOM, 93 numbered sections.
- Initial worktree: dirty, with `.gitignore` and `pyproject.toml` modified and numerous untracked files. All preexisting work was preserved.

## 2. Architecture and files

The implementation adds the isolated `cko.core.provenance` value-domain foundation. Models, typed references, versioning, results, normalization, identity, serializer, validator, factory and operations are separated. Relationship projection is peripheral and imports only public `cko.core.relationships` contracts.

Created production files:

- `src/cko/core/provenance/__init__.py`
- `src/cko/core/provenance/constants.py`
- `src/cko/core/provenance/contracts.py`
- `src/cko/core/provenance/enums.py`
- `src/cko/core/provenance/errors.py`
- `src/cko/core/provenance/factory.py`
- `src/cko/core/provenance/identity.py`
- `src/cko/core/provenance/models.py`
- `src/cko/core/provenance/operations.py`
- `src/cko/core/provenance/references.py`
- `src/cko/core/provenance/relationship_projection.py`
- `src/cko/core/provenance/results.py`
- `src/cko/core/provenance/serializer.py`
- `src/cko/core/provenance/validator.py`
- `src/cko/core/provenance/versioning.py`

Created test/documentation files:

- `tests/test_knowledge_provenance_statement_foundation_spr017.py`
- `CKO_PROVENANCE_STATEMENT_ARCHITECTURE.md`
- `CKO_PROVENANCE_STATEMENT_API.md`
- `CKO_PROVENANCE_STATEMENT_MODEL_GUIDE.md`
- `CKO_PROVENANCE_STATEMENT_SERIALIZATION.md`
- `CKO_PROVENANCE_STATEMENT_OPERATIONS.md`
- `CKO_PROVENANCE_STATEMENT_INTEGRATION.md`
- `SPR017_IMPLEMENTATION_REPORT.md`

Altered shared file: `src/cko/core/__init__.py`, only to add the 36 imports and root exports.

The specification and `SPR017G_VERIFICACAO_FINAL.md` were not altered.

## 3. Public API

The 36 public symbols are located in `cko.core.provenance` and reexported by `cko.core`.

| Family | Symbols |
|---|---|
| Constants | `PROVENANCE_SCHEMA_VERSION`, `PROVENANCE_SERIALIZATION_VERSION`, `PROVENANCE_UUID_NAMESPACE`, `PROVENANCE_VERSION` |
| Enums | `ProvenanceStatementCategory`, `ProvenanceTargetType`, `ProvenanceEntityRole`, `ProvenanceActorType`, `ProvenanceActorRole`, `ProvenanceActivityType`, `ProvenanceEvidenceType` |
| Models | `ProvenanceStatementId`, `ProvenanceStatementIdentity`, `ProvenanceQualifier`, `ProvenanceSubjectRef`, `ProvenanceEntityRef`, `ProvenanceActorRef`, `ProvenanceActivityRef`, `ProvenanceEvidenceRef`, `ProvenanceStatementRef`, `ProvenanceStatementVersion`, `ProvenanceStatement`, `ProvenanceStatementComparisonResult`, `ProvenanceChainValidationResult` |
| Services | `ProvenanceStatementFactory`, `ProvenanceStatementValidator`, `DeterministicProvenanceSerializer`, `ProvenanceOperations` |
| Exceptions | `ProvenanceError`, `ProvenanceValidationError`, `ProvenanceSerializationError`, `ProvenanceFactoryError`, `ProvenanceIdentityError`, `ProvenanceVersionError`, `ProvenanceDigestError`, `ProvenanceChainError` |

Mechanical result: `cko.core.__all__` has 646 entries, 646 unique names and 646 resolved names. The 610 baseline names remain; the 36 candidates are unique and have zero nominal collisions.

`KnowledgeProvenance` remains identical across `cko.core`, `cko.core.knowledge` and `cko.core.knowledge.metadata`, with the same module, signature, frozen/slotted traits and prior behavior.

## 4. Deterministic evidence

| Evidence | Result |
|---|---|
| 13 schemas | frozen, slotted, keyword-only, closed envelopes and V-01–V-13 round-trip approved |
| Seven enums | exact closed values approved; abbreviated aliases rejected |
| CanonicalValue | distinct private array/object representations; NFC collision detection; C-02 equals `[null,true,false,0,-12]` |
| I-01 | `d4e5aadf-9468-59aa-8076-28fe5e91642d` |
| I-02 | target version/digest change preserves I-01 |
| I-03 | `579a17ba-956d-57ba-a48d-4f829e30ee50` |
| I-04 | `2ac58580-c9ec-5345-8eb0-d95f410cba82`; NFC/NFD converge |
| D-01 | 1.309 bytes; `dda22685f6674a51030a4c4eacbb0f4cf5991a8d6d61435c5fa0e9bbb50efd6d`; final 1.385 bytes |
| R-01 IDs | logical `14662ce7-1def-5fe9-8659-0fc5988074ee`; canonical `488066ef-1ba9-5947-a510-993b0df40914`; version `2c7e0eca-280f-58b4-9846-b5c209eb81b5` |
| R-01 bytes | 2.379 bytes; SHA-256 `8a4d2012d7b997f9dfbe3324ed148c2f4cfdd894a3448564fd215d3cdda3b5be` |
| Revision | revisions 1/2/3 map to 1.0.0/1.0.1/1.0.2 with complete previous references |
| Chain | roots, multiple roots, external boundaries, disconnected components and partial chains accepted; self/conflicts/cycles rejected |
| Serialization | structural, semantic and byte-for-byte round-trip approved for all 13 discriminators |
| Services/errors | four services and eight typed exception classes approved with deterministic codes/messages |

## 5. Tests, coverage, build and installation

- Dedicated suite: 30 normative groups, 50 executed cases, all passed.
- SPR-010–017 integration: 225 passed.
- Full regression outside the synchronized Drive temporary tree: 928 passed, two historical failures reproduced, zero new failures.
- Historical failures: `tests/test_file_metadata.py::test_collect_metadata` rejects the preexisting unsupported `calculate_hash=True`; `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved` retains a Windows SQLite handle during teardown.
- Coverage for `cko.core.provenance`: 1.036 statements, 0 missed; 292 branches, 0 partial/missed; 100% lines and 100% branches.
- Architecture gates: import allowlist, forbidden-call scan, no Query/Graph/Index/Corpus/Inventory dependency, frozen/slots, public API and no UUIDv4/clock in projection all passed.
- Deterministic build: exit code zero, 440.069-byte wheel, 280 entries, 15 provenance modules, no tests/cache/bytecode.
- Wheel SHA-256: `A4AEED041D35B227B1BBDF3462B3B819313C4D378A09A74FE6796919807FA698`.
- Isolated installation: passed. Smoke result from installed wheel: 646/646/646 exports, I-01 and D-01 exact, 1.385-byte final envelope.
- Existing canonical wheel in `runtime/reports/build` was not overwritten.

## 6. AC-001–AC-090 matrix

| ID | Status | Evidence |
|---|---|---|
| AC-001 | PASS | isolated namespace import |
| AC-002 | PASS | responsibility/AST review |
| AC-003 | PASS | forbidden-import/call gate |
| AC-004 | PASS | API and seven guides |
| AC-005 | PASS | KnowledgeProvenance identity/signature tests |
| AC-006 | PASS | 610 baseline exports preserved |
| AC-007 | PASS | 13 frozen/slotted models |
| AC-008 | PASS | direct aggregate construction returns PF001 |
| AC-009 | PASS | I-01–I-04 identity tests |
| AC-010 | PASS | required typed subject validation |
| AC-011 | PASS | multiple entity fixtures |
| AC-012 | PASS | actor references remain declarative |
| AC-013 | PASS | single optional activity field |
| AC-014 | PASS | five opaque evidence types |
| AC-015 | PASS | seven closed enums |
| AC-016 | PASS | complete category matrix tests |
| AC-017 | PASS | no reference resolution/I/O |
| AC-018 | PASS | empty/simple/multiple chain fixtures |
| AC-019 | PASS | PC001 self rejection |
| AC-020 | PASS | PC004 direct/mixed cycle rejection |
| AC-021 | PASS | ordered external boundaries |
| AC-022 | PASS | no authorship promotion |
| AC-023 | PASS | revision and derivation separated |
| AC-024 | PASS | evidence and digest separated |
| AC-025 | PASS | digest documented/tested as integrity |
| AC-026 | PASS | exact UUIDv5 vectors |
| AC-027 | PASS | namespace derivation reproduced |
| AC-028 | PASS | subject/category identity changes |
| AC-029 | PASS | revisions preserve identity |
| AC-030 | PASS | version dimensions remain distinct |
| AC-031 | PASS | NFC and strict UTF-8 tests |
| AC-032 | PASS | closed canonical JSON |
| AC-033 | PASS | unknown/duplicate keys rejected |
| AC-034 | PASS | 13 byte-identical round-trips |
| AC-035 | PASS | exact SHA-256 reproduction |
| AC-036 | PASS | permutations preserve digest |
| AC-037 | PASS | semantic mutation changes digest |
| AC-038 | PASS | immutable/stateless operations |
| AC-039 | PASS | no snapshot symbol/module |
| AC-040 | PASS | no builder symbol/module |
| AC-041 | PASS | Relationship only explicit projection |
| AC-042 | PASS | projection loss documented/tested |
| AC-043 | PASS | zero Graph import/update |
| AC-044 | PASS | zero Index update |
| AC-045 | PASS | Corpus stays non-authoritative |
| AC-046 | PASS | Query absent from target/imports |
| AC-047 | PASS | Inventory untouched |
| AC-048 | PASS | only public integration contracts |
| AC-049 | PASS | zero private cross-foundation import |
| AC-050 | PASS | zero reverse dependency/cycle |
| AC-051 | PASS | zero infrastructure dependency |
| AC-052 | PASS | exactly 36 public candidates |
| AC-053 | PASS | zero collision against 610 |
| AC-054 | PASS | namespace/root exports coherent |
| AC-055 | PASS | source inventory mechanically authoritative; legacy catalog intentionally unchanged |
| AC-056 | PASS | dependency topology mechanically verified; external matrix intentionally unchanged |
| AC-057 | PASS | authorized versions preserved: SDK 1.0.0, foundation 1.0.0 |
| AC-058 | PASS | dedicated suite 50/50 |
| AC-059 | PASS | integration SPR-010–017 225/225 |
| AC-060 | PASS | zero new regression; 928 passed |
| AC-061 | PASS | 100% lines/branches |
| AC-062 | PASS | every critical branch executed |
| AC-063 | PASS | AST/dependency/API gates |
| AC-064 | PASS | deterministic build exit zero |
| AC-065 | PASS | wheel modules/content inspected |
| AC-066 | PASS | isolated install and smoke |
| AC-067 | PASS | wheel hash/size/entries recorded |
| AC-068 | PASS | report plus six required guides |
| AC-069 | PASS | old schemas unchanged |
| AC-070 | PASS | no migration added |
| AC-071 | PASS | two historical failures isolated |
| AC-072 | PASS | no later Sprint anticipated |
| AC-073 | PASS | 13 reflected schemas exact |
| AC-074 | PASS | exact subject token vectors |
| AC-075 | PASS | I-02 excludes target version/digest |
| AC-076 | PASS | complete previous revision |
| AC-077 | PASS | ID@revision node keys |
| AC-078 | PASS | supplied-set limitation tested |
| AC-079 | PASS | semantic matrix product coverage |
| AC-080 | PASS | six-digit UTC |
| AC-081 | PASS | bounded integer domain |
| AC-082 | PASS | 13 discriminated envelopes |
| AC-083 | PASS | exact D-01 payload |
| AC-084 | PASS | verify/require behavior distinct |
| AC-085 | PASS | projection calls `from_parts` |
| AC-086 | PASS | no clock/UUIDv4 |
| AC-087 | PASS | exact R-01 bytes twice |
| AC-088 | PASS | seven target ID forms |
| AC-089 | PASS | documentation ownership/content closed |
| AC-090 | PASS | source/wheel/API reconcile at 646 |

All 90 IDs are unique, executable or mechanically inspectable, traced to a fixture/gate and approved.

## 7. Git, scope and readiness

No dependency version, global SDK version, legacy schema, migration, catalog, architecture baseline, preexisting wheel or unrelated Sprint artifact was changed. External documentary divergences (334/346 counts, residual 0.1.0, incomplete matrix and mojibake) remain intentionally untouched.

No commit, push or pull request was performed.

The SHA-256 of this report is calculated after its final write and recorded in the completion chat; embedding the hash of the complete file inside the same file would be self-referential.

Decision: **APTA PARA HOMOLOGAÇÃO**.
