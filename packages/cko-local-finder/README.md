# CKO Local Knowledge Finder

`cko-local-finder` is the independently installable package planned by GOV-010 and architecturally constrained by ADR-008. Version `0.1.0` contains only the P-019-01 package foundation and contract skeleton.

## Status

```text
STATUS: FOUNDATION ONLY
VERSION: 0.1.0
MVP_USABLE: NO
P_019_02_AUTHORIZED: NO
```

The package is typed, has no runtime dependencies, and does not modify or extend the public API of the `cko` distribution.

## Architecture

- `cko_local_finder.domain`: immutable, technology-neutral contract models.
- `cko_local_finder.application`: abstract ports expressed as `typing.Protocol`.
- `cko_local_finder.infrastructure`: reserved namespace for future adapters; currently empty.
- `cko_local_finder.cli`: reserved namespace for future CLI composition; currently empty and has no entry point.

The root package exposes only `__version__`. Domain models and application ports must be imported from their owning modules.

## Not implemented

This foundation does not discover files, calculate hashes, extract documents, persist data, use SQLite or FTS5, search content, expose a functional CLI, or process a real or synthetic corpus. Those capabilities belong to separately authorized future increments P-019-02 through P-019-09.

## Development installation and tests

From an isolated Python environment:

```text
python -m pip install -e packages/cko-local-finder
python -m pytest packages/cko-local-finder/tests
```

These instructions install and test only the foundation. They do not make the MVP usable and do not authorize any later increment.
