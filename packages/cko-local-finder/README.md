# CKO Local Knowledge Finder

`cko-local-finder` is the independently installable package planned by GOV-010 and architecturally constrained by ADR-008. Version `0.1.0` includes the consolidated P-019-01 foundation, P-019-02 synthetic test harness, and the approved P-019-03 internal discovery capability.

## Status

```text
STATUS: P-019-01 THROUGH P-019-03 IMPLEMENTED
VERSION: 0.1.0
MVP_USABLE: NO
P_019_01_STATUS: CONSOLIDATED
P_019_02_STATUS: CONSOLIDATED
P_019_03_STATUS: IMPLEMENTED AFTER HUMAN APPROVAL
P_019_04_AUTHORIZED: NO
```

The package is typed, has no runtime dependencies, and does not modify or extend the public API of the `cko` distribution.

## Architecture

- `cko_local_finder.domain`: immutable, technology-neutral contract models.
- `cko_local_finder.application`: abstract ports plus in-memory discovery and duplicate grouping.
- `cko_local_finder.infrastructure`: confined filesystem discovery and incremental SHA-256 hashing.
- `cko_local_finder.cli`: reserved namespace for future CLI composition; currently empty and has no entry point.

The root package exposes only `__version__`. Domain models and application ports must be imported from their owning modules.

The internal discovery capability requires an explicit local root, ignores hidden files and symlinks by default, recognizes PDF, DOCX, TXT, and Markdown by extension, calculates stable SHA-256 identities, preserves duplicate locations, and continues after isolated file failures.

## Not implemented

There is no functional CLI, text extraction, persistence, SQLite, FTS5, textual search, or final-user workflow. The product is not ready for end use, and P-019-04 is not authorized.

## Development installation and tests

From an isolated Python environment:

```text
python -m pip install -e packages/cko-local-finder
python -m pytest packages/cko-local-finder/tests
```

These instructions exercise internal package capabilities only. They do not make the MVP usable and do not authorize P-019-04 or any later increment.
