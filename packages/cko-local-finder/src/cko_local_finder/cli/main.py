"""Unified argparse command-line interface."""
from __future__ import annotations
import argparse
from collections.abc import Sequence
from contextlib import redirect_stderr, redirect_stdout
import sqlite3
import sys
from typing import TextIO
from cko_local_finder import __version__
from cko_local_finder.cli import runtime
from cko_local_finder.cli.presenters import present
from cko_local_finder.infrastructure.sqlite import RepositoryError

SUCCESS, RECOVERABLE_FAILURE, INVALID_USAGE, NOT_FOUND = 0, 1, 2, 3
DATABASE_FAILURE, RESOURCE_UNAVAILABLE, INTERNAL_FAILURE = 4, 5, 10

def _format(parser: argparse.ArgumentParser) -> None: parser.add_argument("--format", choices=("text", "json"), default="text")
def _database(parser: argparse.ArgumentParser) -> None: parser.add_argument("--database", required=True, metavar="PATH")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cko-local-finder", description="Local document discovery and search")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="ingest a confined local root")
    ingest.add_argument("root", metavar="ROOT"); _database(ingest); _format(ingest)
    ingest.add_argument("--include-hidden", action="store_true"); ingest.add_argument("--follow-symlinks", action="store_true")
    search = commands.add_parser("search", help="search indexed document text")
    search.add_argument("query", metavar="QUERY"); _database(search); _format(search)
    search.add_argument("--limit", type=int, default=20, choices=range(1, 101), metavar="N")
    search.add_argument("--extension"); search.add_argument("--media-type"); search.add_argument("--root")
    search.add_argument("--path-prefix"); search.add_argument("--sha256")
    show = commands.add_parser("show", help="show provenance by SHA-256")
    show.add_argument("sha256", metavar="SHA256"); _database(show); _format(show)
    duplicate = commands.add_parser("duplicates", help="list duplicate locations")
    _database(duplicate); _format(duplicate); duplicate.add_argument("--root")
    report = commands.add_parser("report", help="produce a persisted-state report")
    report.add_argument("report_type", choices=("ingestion", "failures", "duplicates"), metavar="TYPE")
    _database(report); _format(report); report.add_argument("--root")
    return parser

def _dispatch(args: argparse.Namespace):
    values = vars(args).copy(); command = values.pop("command"); output_format = values.pop("format")
    if command == "ingest": result = runtime.ingest(**values)
    elif command == "search": result = runtime.search(**values)
    elif command == "show": result = runtime.show(**values)
    elif command == "duplicates": result = runtime.duplicates(**values)
    else: result = runtime.report(values.pop("report_type"), **values)
    return result, output_format

def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    out, err = stdout or sys.stdout, stderr or sys.stderr
    try:
        with redirect_stdout(out), redirect_stderr(err): args = build_parser().parse_args(argv)
        result, output_format = _dispatch(args); out.write(present(result, output_format))
        return RECOVERABLE_FAILURE if isinstance(result, runtime.IngestResult) and result.recoverable_failures else SUCCESS
    except SystemExit as exc: return int(exc.code or 0)
    except (FileNotFoundError, LookupError) as exc: err.write(f"error: {exc}\n"); return NOT_FOUND
    except runtime.RequiredResourceUnavailable as exc: err.write(f"error: {exc}\n"); return RESOURCE_UNAVAILABLE
    except (RepositoryError, sqlite3.Error): err.write("error: database operation failed\n"); return DATABASE_FAILURE
    except ValueError as exc: err.write(f"error: {exc}\n"); return INVALID_USAGE
    except KeyboardInterrupt: err.write("error: interrupted\n"); return INTERNAL_FAILURE
    except Exception: err.write("error: internal failure\n"); return INTERNAL_FAILURE

if __name__ == "__main__": raise SystemExit(main())
