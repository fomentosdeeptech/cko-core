# CKO Local Knowledge Finder

`cko-local-finder` is the independently installable, local-only document finder planned by GOV-010 and architecturally constrained by ADR-008. Version `0.1.0` is the end-to-end validated SPR-019 MVP for a controlled local pilot.

## Status

```text
STATUS: SPR-019 IMPLEMENTED / VALIDATED / CONSOLIDATED
VERSION: 0.1.0
MVP_USABLE: YES — CONTROLLED LOCAL PILOT ONLY
P_019_01_STATUS: CONSOLIDATED
P_019_02_STATUS: CONSOLIDATED
P_019_03_STATUS: CONSOLIDATED
P_019_04_STATUS: CONSOLIDATED
P_019_05_STATUS: CONSOLIDATED
P_019_06_STATUS: CONSOLIDATED
P_019_07_STATUS: CONSOLIDATED
P_019_08_STATUS: CONSOLIDATED
P_019_09_STATUS: IMPLEMENTED / VALIDATED / CONSOLIDATED
```

The package is typed, depends directly only on `pypdf` and `python-docx`, and does not modify or extend the public API of the `cko` distribution.

## Architecture

- `cko_local_finder.domain`: immutable, technology-neutral contract models.
- `cko_local_finder.application`: abstract ports plus discovery, extraction, indexing, rebuild, and search orchestration.
- `cko_local_finder.infrastructure`: confined discovery, extraction, SQLite persistence, and safe FTS5 search execution.
- `cko_local_finder.cli`: argparse parsing, adapter composition, presentation, and exit codes.

The root package exposes only `__version__`. Domain models and application ports must be imported from their owning modules.

The internal discovery capability requires an explicit local root, ignores hidden files and symlinks by default, recognizes PDF, DOCX, TXT, and Markdown by extension, calculates stable SHA-256 identities, preserves duplicate locations, and continues after isolated file failures.

Discovery reports can be persisted in an explicit SQLite database as derived, rebuildable state. Schema version 1 stores SHA-256 documents, multiple locations, sanitized issues, and a reserved empty extraction structure. Transactions, checksummed migrations, foreign keys, idempotent updates, rollback, path reassignment, and persisted duplicate lookup are supported. FTS5 availability is verified with a temporary probe only; no persistent text index exists.

Internal text extraction supports UTF-8 TXT, UTF-8 Markdown, textual PDF through `pypdf`, and DOCX paragraphs and tables through `python-docx`. Extraction results, statuses, technical metadata, and isolated failures are persisted transactionally and idempotently. PDF files without text return `NO_TEXT`; OCR is never attempted. DOCX ZIP structure and safety limits are checked before parsing.

Schema version 2 adds one persistent FTS5 table using `unicode61 remove_diacritics 2`, a derived index projection, strict synchronization triggers, idempotent reindexing, and full rebuild from persisted state without rereading source files. Internal text search uses literal parameterized queries, BM25 ranking with deterministic tie-breaking, bounded highlighted snippets, pagination, and explicit extension, media type, root, relative-path prefix, and SHA-256 filters.

Schema version 3 preserves optional document SHA-256 and authorized root on processing issues. Provenance joins SHA-256 identity to every known relative location, extraction, indexing, issues, and duplicate evidence without using absolute paths as identity. Historical issues whose origin cannot be proved remain explicitly unresolved rather than being guessed.

Internal ingestion, failure, and duplicate reports are typed values serializable to deterministic UTF-8 JSON with sorted keys and an explicit caller-supplied timestamp. Pure declarative mappings describe the correspondence to `core.documents` and `core.provenance`; the package neither imports nor writes to CKO Core.

## Installation and help

Install the wheel in a Python 3.13 or newer virtual environment. The installation provides one executable:

```text
python -m pip install cko_local_finder-0.1.0-py3-none-any.whl
cko-local-finder --help
cko-local-finder --version
```

Every persistent command requires an explicit `--database PATH`. Ingest creates the database when its parent directory exists; read commands require an existing database. The database contains derived extracted text and should be stored outside the source collection and never committed to Git.

## Commands

Windows examples:

```text
cko-local-finder ingest C:\Documents\Knowledge --database C:\CKO\data\knowledge.db
cko-local-finder search "project evidence" --database C:\CKO\data\knowledge.db --limit 20
cko-local-finder show 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef --database C:\CKO\data\knowledge.db
cko-local-finder duplicates --database C:\CKO\data\knowledge.db
cko-local-finder report ingestion --root C:\Documents\Knowledge --database C:\CKO\data\knowledge.db
cko-local-finder report failures --database C:\CKO\data\knowledge.db --format json
cko-local-finder report duplicates --database C:\CKO\data\knowledge.db
```

`search` supports `--extension`, `--media-type`, `--root`, `--path-prefix`, `--sha256`, and a limit from 1 through 100. All commands support stable human-readable `text` output and deterministic UTF-8 `json` output. Results go to stdout and safe diagnostics go to stderr.

Hidden files are ignored unless `--include-hidden` is supplied. Symbolic links are never followed: the default ignores them and `--follow-symlinks` fails closed because that policy is not implemented. Root confinement remains mandatory. Source documents are always read-only.

Exit codes are: `0` success, `1` ingestion completed with recoverable failures, `2` invalid usage or argument, `3` requested root/database/document not found, `4` database or migration failure, `5` required capability such as FTS5 unavailable, and `10` safely handled unexpected failure.

## Privacy and MVP limitations

Processing is local: the CLI performs no network calls, telemetry, or hidden logging. Full document content is not printed. The SQLite database does contain extracted content and must be protected accordingly.

## Controlled pilot procedure

Begin with only 20–50 explicitly authorized, non-confidential documents in a dedicated folder. Create a Python 3.13+ virtual environment, install the validated wheel, and place the derived SQLite database in a protected directory outside both the source collection and every Git repository. Then run, in order:

```text
cko-local-finder ingest C:\Pilot\AuthorizedDocuments --database C:\PilotData\cko-finder.db --format json
cko-local-finder search "known term" --database C:\PilotData\cko-finder.db --limit 20
cko-local-finder show <64-character-sha256> --database C:\PilotData\cko-finder.db --format json
cko-local-finder duplicates --database C:\PilotData\cko-finder.db --format json
cko-local-finder report ingestion --root C:\Pilot\AuthorizedDocuments --database C:\PilotData\cko-finder.db --format json
cko-local-finder report failures --database C:\PilotData\cko-finder.db --format json
cko-local-finder report duplicates --database C:\PilotData\cko-finder.db --format json
```

Review provenance, duplicate locations, and every recoverable failure before relying on results. Do not use confidential, personal, regulated, or production documents in the initial pilot. Back up or delete the derived database according to the operator's local data-handling rules.

## Not implemented

There is no OCR, semantic or vector search, RAG, remote access, watcher, GUI, macro execution, or symlink traversal. Search is lexical FTS5, supported source formats are textual PDF, DOCX, UTF-8 TXT, and Markdown, and isolated corrupt/invalid files are reported rather than repaired. The readiness decision authorizes only a controlled local pilot; it is not approval for a public deployment, real confidential corpus, federation, or P-018-02.

## Development installation and tests

From an isolated Python environment:

```text
python -m pip install -e packages/cko-local-finder
python -m pytest packages/cko-local-finder/tests
```

These instructions exercise the package and CLI. They do not authorize P-018-02 or any later product increment.
