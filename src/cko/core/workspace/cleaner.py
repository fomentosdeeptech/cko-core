"""Safe discovery and cleanup of temporary development artifacts."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import WorkspaceManager


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CleanResult:
    """Immutable report for one cleanup operation."""

    operation: str
    candidates: tuple[Path, ...]
    removed: tuple[Path, ...]
    dry_run: bool

    @property
    def count(self) -> int:
        """Return the number of artifacts removed or proposed."""
        return len(self.candidates) if self.dry_run else len(self.removed)


class TemporaryFileManager:
    """Discover and safely remove only approved temporary artifacts."""

    def __init__(self, manager: WorkspaceManager) -> None:
        self.manager = manager
        self.paths = manager.paths

    def _is_within(self, candidate: Path, parent: Path) -> bool:
        try:
            candidate.relative_to(parent)
            return True
        except ValueError:
            return False

    def is_safe(self, candidate: Path) -> bool:
        """Return whether a candidate is contained and outside protected data."""
        try:
            resolved = candidate.resolve()
        except OSError:
            return False
        root = self.paths.root.resolve()
        if resolved == root or not self._is_within(resolved, root):
            return False
        return not any(
            resolved == protected.resolve()
            or self._is_within(resolved, protected.resolve())
            for protected in self.paths.permanent_directories
        )

    def _walk(self) -> Iterable[Path]:
        for candidate in self.paths.root.rglob("*"):
            if any(
                candidate == protected
                or self._is_within(candidate, protected)
                for protected in self.paths.permanent_directories
            ):
                continue
            yield candidate

    def python_cache_candidates(self) -> tuple[Path, ...]:
        """Find ``__pycache__``, bytecode and pytest cache artifacts."""
        selected = [
            item for item in self._walk()
            if item.name == "__pycache__"
            or item.name == ".pytest_cache"
            or (item.is_file() and item.suffix.lower() in {".pyc", ".pyo"})
        ]
        return self._normalize(selected)

    def cover_candidates(self) -> tuple[Path, ...]:
        """Find legacy ``.cover`` files or directories."""
        return self._normalize(item for item in self._walk() if item.name == ".cover")

    def temp_candidates(self) -> tuple[Path, ...]:
        """Find recognized legacy project temporary directories."""
        selected = []
        for item in self._walk():
            name = item.name.casefold()
            if item.is_dir() and (
                name == "temp"
                or name == ".pytest_tmp"
                or name == "pytest_tmp"
                or name.endswith("_pytest_tmp")
                or name.endswith("_test_temp")
            ):
                selected.append(item)
        return self._normalize(selected)

    def trace_candidates(self) -> tuple[Path, ...]:
        """Find legacy trace directories outside the canonical trace folder."""
        return self._normalize(
            item for item in self._walk()
            if item.is_dir() and item.name.casefold() in {"trace", "traces"}
        )

    def contents(self, directory: Path) -> tuple[Path, ...]:
        """Return direct children of a canonical temporary directory."""
        if not directory.exists():
            return ()
        return self._normalize(directory.iterdir())

    def _normalize(self, candidates: Iterable[Path]) -> tuple[Path, ...]:
        safe = {item for item in candidates if self.is_safe(item)}
        ordered = sorted(safe, key=lambda item: (len(item.parts), str(item).casefold()))
        roots: list[Path] = []
        for item in ordered:
            if not any(self._is_within(item, parent) for parent in roots):
                roots.append(item)
        return tuple(roots)

    def remove(self, candidates: Iterable[Path], *, dry_run: bool) -> tuple[Path, ...]:
        """Remove approved candidates without following directory symlinks."""
        removed: list[Path] = []
        for candidate in self._normalize(candidates):
            if dry_run:
                continue
            try:
                if candidate.is_symlink() or candidate.is_file():
                    candidate.unlink()
                elif candidate.is_dir():
                    shutil.rmtree(candidate)
                else:
                    continue
            except FileNotFoundError:
                continue
            removed.append(candidate)
        return tuple(removed)


class WorkspaceCleaner:
    """Expose canonical cleanup operations with dry-run and audit logging."""

    def __init__(self, manager: WorkspaceManager, *, dry_run: bool = False) -> None:
        self.manager = manager
        self.paths = manager.paths
        self.dry_run_mode = dry_run
        self.temporary = TemporaryFileManager(manager)

    def _execute(
        self,
        operation: str,
        candidates: Iterable[Path],
        event: str,
    ) -> CleanResult:
        normalized = self.temporary._normalize(candidates)
        removed = self.temporary.remove(normalized, dry_run=self.dry_run_mode)
        self.manager.create()
        result = CleanResult(operation, normalized, removed, self.dry_run_mode)
        LOGGER.info(
            operation.replace("_", " "),
            extra={
                "event": event,
                "context": {
                    "dry_run": self.dry_run_mode,
                    "count": result.count,
                    "paths": [str(item) for item in normalized],
                },
            },
        )
        return result

    def clean_temp(self) -> CleanResult:
        """Clear the canonical temporary directory while preserving it."""
        legacy = tuple(
            item for item in self.temporary.temp_candidates()
            if item != self.paths.temp
        )
        return self._execute(
            "clean_temp",
            (*self.temporary.contents(self.paths.temp), *legacy),
            "workspace_cleaned",
        )

    def clean_cache(self) -> CleanResult:
        """Clear canonical and legacy coverage caches."""
        candidates = (
            *self.temporary.contents(self.paths.cache),
            *self.temporary.cover_candidates(),
        )
        return self._execute("clean_cache", candidates, "cache_removed")

    def clean_trace(self) -> CleanResult:
        """Clear the canonical trace directory while preserving it."""
        legacy = tuple(
            item for item in self.temporary.trace_candidates()
            if item != self.paths.traces
        )
        return self._execute(
            "clean_trace",
            (*self.temporary.contents(self.paths.traces), *legacy),
            "trace_removed",
        )

    def clean_python_cache(self) -> CleanResult:
        """Remove Python bytecode and pytest cache artifacts."""
        return self._execute(
            "clean_python_cache",
            self.temporary.python_cache_candidates(),
            "cache_removed",
        )

    def clean(self) -> CleanResult:
        """Run every cleanup category and return one deduplicated report."""
        legacy_temp = tuple(
            item for item in self.temporary.temp_candidates()
            if item != self.paths.temp
        )
        legacy_trace = tuple(
            item for item in self.temporary.trace_candidates()
            if item != self.paths.traces
        )
        candidates = (
            *self.temporary.contents(self.paths.temp),
            *self.temporary.contents(self.paths.cache),
            *self.temporary.contents(self.paths.traces),
            *legacy_temp,
            *legacy_trace,
            *self.temporary.cover_candidates(),
            *self.temporary.python_cache_candidates(),
        )
        return self._execute("clean", candidates, "workspace_cleaned")

    def dry_run(self) -> CleanResult:
        """Preview a complete cleanup without modifying the workspace."""
        preview = WorkspaceCleaner(self.manager, dry_run=True)
        return preview.clean()
