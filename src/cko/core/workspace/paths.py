"""Centralized and immutable paths for the local development runtime."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RuntimePaths:
    """Canonical locations used by development and build infrastructure."""

    root: Path
    runtime: Path
    temp: Path
    cache: Path
    traces: Path
    logs: Path
    reports: Path
    database: Path
    snapshots: Path

    @classmethod
    def from_root(cls, root: str | Path) -> RuntimePaths:
        """Create normalized canonical paths below ``root``."""
        normalized = Path(root).expanduser().resolve()
        runtime = normalized / "runtime"
        return cls(
            root=normalized,
            runtime=runtime,
            temp=runtime / "temp",
            cache=runtime / "cache",
            traces=runtime / "traces",
            logs=runtime / "logs",
            reports=runtime / "reports",
            database=runtime / "database",
            snapshots=runtime / "snapshots",
        )

    @classmethod
    def discover(
        cls,
        start: str | Path | None = None,
        *,
        environ: dict[str, str] | None = None,
    ) -> RuntimePaths:
        """Locate the project root using an override or a ``pyproject.toml``."""
        environment = os.environ if environ is None else environ
        override = environment.get("CKO_WORKSPACE_ROOT")
        if override:
            return cls.from_root(override)
        candidate = Path.cwd() if start is None else Path(start)
        candidate = candidate.expanduser().resolve()
        if candidate.is_file():
            candidate = candidate.parent
        for directory in (candidate, *candidate.parents):
            if (directory / "pyproject.toml").is_file():
                return cls.from_root(directory)
        raise FileNotFoundError(
            f"CKO workspace not found from {candidate}; "
            "set CKO_WORKSPACE_ROOT explicitly"
        )

    @property
    def canonical_directories(self) -> tuple[Path, ...]:
        """Return the complete directory structure in creation order."""
        return (
            self.runtime,
            self.temp,
            self.cache,
            self.traces,
            self.logs,
            self.reports,
            self.database,
            self.snapshots,
        )

    @property
    def permanent_directories(self) -> tuple[Path, ...]:
        """Return directories that cleanup operations must never modify."""
        return (
            self.database,
            self.reports,
            self.snapshots,
            self.logs,
            self.root / "database",
            self.root / "reports",
            self.root / "snapshots",
            self.root / "logs",
        )
