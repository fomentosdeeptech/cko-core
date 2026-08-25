# SPR-020 — INC-GUI-001A Implementation Report

## Outcome

`INC-GUI-001A` introduces a typed, presentation-neutral application facade and one shared
composition root for the existing CLI and a possible future desktop adapter. The CLI uses
the same composed application without subprocess invocation or duplicated business rules.
No graphical interface was implemented.

## Architecture and boundaries

- `application/facade.py` owns immutable requests, results, progress events and use-case orchestration.
- `bootstrap.py` composes filesystem discovery, extractors and the SQLite repository.
- `cli/runtime.py` translates CLI calls to facade requests; presenters remain in the CLI.
- extraction protocols and recoverable errors are application contracts specialized by infrastructure.
- search limits belong to application validation; discovery receives its production scanner from bootstrap.
- application has zero static imports of infrastructure, CLI or GUI; bootstrap imports neither CLI nor GUI.
- the facade contains no SQL and has no presenter dependency.

The 13 progress event kinds are the authorized stage-boundary events. Counts appear only
after the corresponding stage produces them. No percentage, time estimate, cancellation
token or cancellation state was added. A late unexpected extraction failure triggers
indexing of already persisted successes before propagation and omits
`EXTRACTION_COMPLETED`.

## Closed allowlist

Exactly the 13 authorized paths were used: nine existing files modified and four files
created. No configuration, dependency, version, schema, `src/cko`, `cko_fcp`, GUI or asset
path changed.

## Validation

- preflight Local Finder baseline: `179 passed, 3 skipped` (182 collected);
- post-change Local Finder suite: `182 passed, 3 skipped` (185 collected);
- new tests: 3;
- dedicated facade/architecture/scope selection: `12 passed`;
- late partial failure: one prior success persisted, indexed and searchable; CLI returned
  nonzero and disclosed no traceback, SQL or document content;
- reingestion and idempotency, search, provenance, reports, duplicates, CLI and end-to-end
  behavior are covered by the passing integral suite;
- packaging, isolated installation, installed CLI, coexistence and reproducibility gates
  were run in external temporary directories.

## Compatibility invariants

```text
SDK_VERSION: 1.0.0
PUBLIC_API_COUNTS: 646 / 646 / 646
PUBLIC_API_FINGERPRINT: d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232
PUBLIC_API_IMPACT: NONE
LOCAL_FINDER_VERSION: 0.1.0
LOCAL_FINDER_PUBLIC_API_COUNT: 1
LOCAL_FINDER_PUBLIC_API_SYMBOLS: __version__
SQLITE_SCHEMA_VERSION: 3
SCHEMA_MIGRATION_ADDED: NO
DEPENDENCY_CHANGE_COUNT: 0
PYSIDE6_ADDED: NO
GUI_FILES_CREATED: 0
```

Only synthetic corpora, synthetic SQLite databases and external temporary directories
were used. Original documents were not mutated. The real pilot database, document root
and document contents were not accessed.

## Next increment

No next graphical increment is authorized by this report. GUI technology, threading,
cancellation, packaging changes and `P-018-02` remain outside the authorization.
