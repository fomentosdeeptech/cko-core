# SPR-019 — P-019-08 Unified CLI Validation Report

## Scope and verdict

P-019-08 implements the unified `cko-local-finder` command-line interface and only composes the ratified P-019-03 through P-019-07 capabilities. P-019-09 and P-018-02 were not executed.

```text
P_019_08_STATUS: IMPLEMENTED / VALIDATED / CONSOLIDATED
SPR_019_STATUS: IN_PROGRESS / P-019-01 THROUGH P-019-08 CONSOLIDATED
P_019_09_STATUS: PLANNED / NOT AUTHORIZED
P_019_09_AUTHORIZED: NO
P_018_02_AUTHORIZED: NO
```

## Delivered interface

The package registers exactly one script, `cko-local-finder = cko_local_finder.cli.main:main`, using standard-library `argparse`. The five commands are:

```text
cko-local-finder ingest ROOT --database DATABASE
cko-local-finder search QUERY --database DATABASE
cko-local-finder show SHA256 --database DATABASE
cko-local-finder duplicates --database DATABASE
cko-local-finder report {ingestion,failures,duplicates} --database DATABASE
```

Text and deterministic UTF-8 JSON presenters write results to stdout. Safe diagnostics write to stderr. Stable exit codes are 0, 1, 2, 3, 4, 5, and 10. The CLI contains no direct SQL, hashing, discovery, extraction, duplicate grouping, provenance construction, or report calculation.

## Test evidence

The preimplementation baseline ran in a temporary Python 3.13 virtual environment outside the repository:

```text
PREEXISTING_TEST_COUNT: 150
PREEXISTING_RESULT: 148 PASSED / 2 SKIPPED
P_019_08_TEST_COUNT: 16
TOTAL_LOCAL_FINDER_TEST_COUNT: 166
FINAL_RESULT: 164 PASSED / 2 SKIPPED
NEW_SKIP_OR_XFAIL_COUNT: 0
```

The final suite covers parsing, help/version, every subcommand, required and invalid arguments, stdout/stderr separation, exit codes, text/JSON, Unicode, final newline, safe diagnostics, ingestion, idempotency, isolated failure continuation, search, filters, snippets, show, duplicates, reports, schema migration, FTS5 handling, architecture, scope, package identity, and entry-point metadata. P-019-01 through P-019-07 regressions remained green within the full suite.

## Installed smoke evidence

Two isolated source copies were built outside the repository with a fixed `SOURCE_DATE_EPOCH`. The two wheel SHA-256 values were identical. The two sdists contained 38 of 38 files with identical content hashes, matching the reproducibility method ratified in P-019-02 and P-019-03.

The wheel was installed into a fresh external virtual environment. The following portable smoke sequence passed against a synthetic two-location corpus and a temporary database:

```text
cko-local-finder --version
cko-local-finder --help
cko-local-finder ingest <synthetic-root> --database <temporary-database>
cko-local-finder search innovation --database <temporary-database>
cko-local-finder duplicates --database <temporary-database>
cko-local-finder report failures --database <temporary-database>
```

```text
WHEEL_BUILD_STATUS: PASS
WHEEL_REPRODUCIBILITY: PASS — IDENTICAL ARTIFACT SHA-256
SDIST_BUILD_STATUS: PASS
SDIST_REPRODUCIBILITY: PASS — 38/38 FILE CONTENT HASHES IDENTICAL
ISOLATED_INSTALL_STATUS: PASS
INSTALLED_ENTRY_POINT_STATUS: PASS
SMOKE_VERSION_STATUS: PASS
SMOKE_HELP_STATUS: PASS
SMOKE_INGEST_STATUS: PASS
SMOKE_SEARCH_STATUS: PASS
SMOKE_DUPLICATES_STATUS: PASS
SMOKE_REPORT_STATUS: PASS
PIP_CHECK_STATUS: PASS
```

CKO 1.0.0, cko-fcp 0.1.0, and cko-local-finder 0.1.0 were installed together from temporary copies/artifacts. All three namespaces imported simultaneously and `pip check` reported no broken requirements.

## Architecture, API, and safety

```text
SQLITE_SCHEMA_VERSION: 3
MIGRATION_ADDED: NO
RUNTIME_DEPENDENCY_COUNT: 2
ENTRY_POINT_COUNT: 1
CLI_BUSINESS_RULE_COUNT: 0
CLI_DIRECT_SQL_COUNT: 0
NETWORK_CALL_COUNT: 0
TELEMETRY_STATUS: ABSENT
SOURCE_DOCUMENT_MUTATION_COUNT: 0
SDK_VERSION: 1.0.0
PUBLIC_API_COUNTS: 646 / 646 / 646
PUBLIC_API_FINGERPRINT: d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232
PUBLIC_API_IMPACT: NONE
BREAKING_CHANGE: NO
SRC_CKO_CHANGES: 0
LOCAL_FINDER_VERSION: 0.1.0
LOCAL_FINDER_PUBLIC_API_COUNT: 1
LOCAL_FINDER_PUBLIC_API_SYMBOLS: __version__
```

No traceback, SQL, ANSI sequence, credential, environment value, document body, hidden log, database, distribution artifact, virtual environment, or new egg-info is retained in the repository. Absolute paths are emitted only when explicitly supplied/authorized as the processed root or database location; document locations remain root plus confined relative path.

## Boundary

This validation consolidates only P-019-08. It does not declare final MVP readiness, use personal documents, start a human pilot, authorize P-019-09, or authorize P-018-02.
