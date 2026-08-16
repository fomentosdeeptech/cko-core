# SPR-019 — CKO Local Knowledge Finder MVP Implementation Plan

## 1. Identification and authority

```text
SPRINT: SPR-019
PRODUCT: CKO Local Knowledge Finder
DISTRIBUTION: cko-local-finder
IMPORT_NAMESPACE: cko_local_finder
EXPECTED_PACKAGE_LOCATION: packages/cko-local-finder/
SPRINT_STATUS: PLANNED / HUMAN_RATIFIED / IMPLEMENTATION_NOT_STARTED
IMPLEMENTATION_AUTHORIZATION: INCREMENT_SPECIFIC_ONLY
```

This human-ratified planning document is aligned with [GOV-010](../governance/GOV-010_CKO_PRODUCT_DIRECTION_AND_LOCAL_KNOWLEDGE_FINDER_MVP.md), [ADR-008](../adr/ADR-008_CKO_LOCAL_KNOWLEDGE_FINDER_MVP_ARCHITECTURE.md), the read-only findings of `AUD-MVP-001`, and the canonical [Sprint index](INDEX.md). It allocates and plans SPR-019 but authorizes no implementation.

```text
GOV_010_ALIGNMENT: PASS
ADR_008_ALIGNMENT: PASS
AUD_MVP_001_ALIGNMENT: PASS
MVP_IMPLEMENTATION_AUTHORIZED: NO
P_019_01_AUTHORIZED: NO — REQUIRES SEPARATE COMMAND
P_018_02_AUTHORIZED: NO
```

## 2. Functional objective

Plan a local MVP that can receive an authorized folder; safely discover supported files; calculate SHA-256; identify byte-for-byte duplicates and multiple locations; extract textual PDF, DOCX, TXT, and Markdown; persist records and derived content in SQLite; index content with SQLite FTS5; execute textual search; and display origin, hash, snippets, and provenance.

The planned command surface is:

```text
cko-local-finder ingest
cko-local-finder search
cko-local-finder show
cko-local-finder duplicates
cko-local-finder report
```

## 3. Planned increments

Exactly nine increments compose the plan. Each remains `PLANNED / NOT AUTHORIZED` and requires a separate human mandate.

### P-019-01 — Package Foundation and Contract Skeleton

```text
P_019_01_STATUS: PLANNED / NOT AUTHORIZED
```

Plan the initial `cko-local-finder` distribution and `cko_local_finder` namespace at `packages/cko-local-finder/`; separate domain, application, infrastructure, and CLI layers; define minimal ports and packaging; validate isolated and joint installation; and preserve the Core and its public API.

### P-019-02 — Synthetic Corpus and Test Harness

```text
P_019_02_STATUS: PLANNED / NOT AUTHORIZED
```

Plan a synthetic corpus with textual PDF, DOCX, TXT, Markdown, an empty file, a corrupted file, an unsupported format, byte-for-byte duplicates, and path and symlink cases. It must contain no personal data or real documents.

### P-019-03 — Safe Discovery, Identity and Duplicate Detection

```text
P_019_03_STATUS: PLANNED / NOT AUTHORIZED
```

Plan confined discovery, path normalization, hidden-file handling, an explicit symlink policy, SHA-256 identity, multiple-location tracking, duplicate detection, and continuation after an isolated failure.

### P-019-04 — Versioned SQLite Persistence

```text
P_019_04_STATUS: PLANNED / NOT AUTHORIZED
```

Plan a minimal document schema and versioned migrations for documents, locations, hashes, extractions, metadata, and errors; require idempotency, rollback, reconstruction, and explicit FTS5 availability verification.

### P-019-05 — Document Extraction

```text
P_019_05_STATUS: PLANNED / NOT AUTHORIZED
```

Plan TXT and Markdown extraction with the standard library, textual PDF extraction with `pypdf`, and DOCX extraction with `python-docx`; define size limits and handling for empty or corrupted files; record extractor identity and version. OCR is out of scope.

### P-019-06 — Text Index, Search, Ranking and Snippets

```text
P_019_06_STATUS: PLANNED / NOT AUTHORIZED
```

Plan SQLite FTS5 indexing, filters, deterministic ranking, snippets, rebuild, and a diagnostic path when FTS5 is unavailable. Embeddings and RAG are excluded.

### P-019-07 — Provenance and Reporting

```text
P_019_07_STATUS: PLANNED / NOT AUTHORIZED
```

Plan provenance for origin, hash, location, and extraction process; define the minimum mapping to `core.documents` and `core.provenance`; and specify ingestion, failure, and duplication reports without changing the Core.

### P-019-08 — Unified CLI

```text
P_019_08_STATUS: PLANNED / NOT AUTHORIZED
```

Plan the future `ingest`, `search`, `show`, `duplicates`, and `report` commands, including arguments, stdout, stderr, and exit codes. The CLI will orchestrate use cases and contain no business rules.

### P-019-09 — End-to-End Validation and MVP Readiness

```text
P_019_09_STATUS: PLANNED / NOT AUTHORIZED
```

Plan end-to-end evidence for ingestion, idempotency, search, duplication, isolated failure, reconstruction, isolated and joint installation, Core protection, and readiness for a controlled local pilot.

## 4. Dependency chain

```text
P-019-01
→ P-019-02
→ P-019-03
→ P-019-04
→ P-019-05
→ P-019-06
→ P-019-07
→ P-019-08
→ P-019-09
```

No increment may begin through dependency implication. Each requires its own explicit human mandate; the first possible future authorization must address only `P-019-01`.

## 5. Permanent gates

Every future increment must independently prove:

```text
SDK_VERSION: 1.0.0
PUBLIC_API_COUNTS: 646 / 646 / 646
PUBLIC_API_FINGERPRINT: d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232
PUBLIC_API_IMPACT: NONE
BREAKING_CHANGE: NO
UNAUTHORIZED_SRC_CKO_CHANGES: 0
P_018_02_AUTHORIZED: NO
```

It must also use a closed path list and controlled staging; run dedicated and packaging tests; introduce zero secrets, tracked databases, tracked builds, or personal documents in the corpus; preserve preexisting artifacts; and use an atomic commit with push only when expressly authorized.

## 6. Explicitly out of scope and not authorized

- GUI
- OCR
- embeddings
- RAG
- generative AI
- semantic search
- remote sources
- cloud synchronization
- federation
- continuous watcher
- autonomous agents
- remote telemetry
- public deployment
- any public API change
- P-018-02

## 7. Authorization boundary

```text
PLANNED_INCREMENT_COUNT: 9
MVP_IMPLEMENTATION_AUTHORIZED: NO
P_019_01_AUTHORIZED: NO — REQUIRES SEPARATE COMMAND
P_019_02_AUTHORIZED: NO
P_019_03_AUTHORIZED: NO
P_019_04_AUTHORIZED: NO
P_019_05_AUTHORIZED: NO
P_019_06_AUTHORIZED: NO
P_019_07_AUTHORIZED: NO
P_019_08_AUTHORIZED: NO
P_019_09_AUTHORIZED: NO
P_018_02_AUTHORIZED: NO
```

This plan must not be treated as a command to create the package, code, tests, fixtures, a SQLite database, migrations, or any implementation artifact.
