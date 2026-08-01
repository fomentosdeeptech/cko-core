"""Command line entry point for canonical workspace operations."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Sequence

from cko.core.logging import configure_logging

from .manager import WorkspaceManager
from .validator import EnvironmentValidator


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cko-workspace")
    parser.add_argument("--root", type=Path, help="explicit CKO CORE root")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init", help="create the canonical runtime tree")
    subparsers.add_parser("validate", help="validate the local environment")
    build = subparsers.add_parser("build", help="build a deterministic wheel")
    build.add_argument("--output", type=Path)
    for name in (
        "clean", "clean-temp", "clean-cache", "clean-trace",
        "clean-python-cache",
    ):
        child = subparsers.add_parser(name, help=f"run {name}")
        child.add_argument("--dry-run", action="store_true")
    return parser


def _print(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv: Sequence[str] | None = None) -> int:
    """Execute one workspace command and return a process exit code."""
    arguments = _parser().parse_args(argv)
    configure_logging(logging.INFO)
    manager = WorkspaceManager(arguments.root)
    if arguments.command == "init":
        created = manager.create()
        _print({"created": [str(item) for item in created]})
        return 0
    if arguments.command == "validate":
        result = EnvironmentValidator(manager).validate()
        _print({
            "valid": result.valid,
            "checks": [
                {
                    "name": item.name,
                    "passed": item.passed,
                    "value": item.value,
                    "requirement": item.requirement,
                }
                for item in result.checks
            ],
        })
        return 0 if result.valid else 1
    if arguments.command == "build":
        from .build import build_wheel

        result = build_wheel(manager, arguments.output)
        _print({"artifact": str(result.artifact), "files": result.files})
        return 0
    cleaner = manager.cleaner(dry_run=arguments.dry_run)
    methods = {
        "clean": cleaner.clean,
        "clean-temp": cleaner.clean_temp,
        "clean-cache": cleaner.clean_cache,
        "clean-trace": cleaner.clean_trace,
        "clean-python-cache": cleaner.clean_python_cache,
    }
    result = methods[arguments.command]()
    _print({
        "operation": result.operation,
        "dry_run": result.dry_run,
        "count": result.count,
        "paths": [str(item) for item in result.candidates],
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
