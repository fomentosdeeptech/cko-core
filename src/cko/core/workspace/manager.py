"""Creation, location and permission management for the CKO workspace."""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path

from .paths import RuntimePaths


LOGGER = logging.getLogger(__name__)


class WorkspaceManager:
    """Create and maintain the canonical local development workspace."""

    def __init__(
        self,
        root: str | Path | None = None,
        *,
        paths: RuntimePaths | None = None,
    ) -> None:
        if root is not None and paths is not None:
            raise ValueError("provide root or paths, not both")
        self.paths = paths or (
            RuntimePaths.discover() if root is None else RuntimePaths.from_root(root)
        )

    def locate(self, name: str) -> Path:
        """Return one canonical path by its stable configuration name."""
        allowed = {
            "root", "runtime", "temp", "cache", "traces", "logs",
            "reports", "database", "snapshots",
        }
        if name not in allowed:
            raise KeyError(f"unknown workspace path: {name}")
        return getattr(self.paths, name)

    def create(self) -> tuple[Path, ...]:
        """Create missing canonical directories and return those created."""
        created: list[Path] = []
        for directory in self.paths.canonical_directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                created.append(directory)
            elif not directory.is_dir():
                raise NotADirectoryError(f"workspace path is not a directory: {directory}")
        LOGGER.info(
            "workspace created",
            extra={
                "event": "workspace_created",
                "context": {
                    "root": str(self.paths.root),
                    "created": [str(item) for item in created],
                },
            },
        )
        return tuple(created)

    def validate_permissions(self) -> bool:
        """Verify write, flush and removal permissions in the temporary area."""
        self.create()
        descriptor: int | None = None
        probe: str | None = None
        try:
            descriptor, probe = tempfile.mkstemp(
                prefix=".cko-permission-",
                suffix=".tmp",
                dir=self.paths.temp,
            )
            os.write(descriptor, "CKO UTF-8: validação".encode("utf-8"))
            os.close(descriptor)
            descriptor = None
            if Path(probe).read_text(encoding="utf-8") != "CKO UTF-8: validação":
                return False
            Path(probe).unlink()
            probe = None
            return True
        except OSError:
            return False
        finally:
            if descriptor is not None:
                os.close(descriptor)
            if probe is not None:
                try:
                    Path(probe).unlink()
                except OSError:
                    pass

    def cleaner(self, *, dry_run: bool = False) -> WorkspaceCleaner:
        """Create a cleaner bound to this workspace."""
        from .cleaner import WorkspaceCleaner

        return WorkspaceCleaner(self, dry_run=dry_run)

    def clean(self, *, dry_run: bool = False) -> CleanResult:
        """Clean all temporary artifacts while preserving permanent data."""
        from .cleaner import CleanResult

        return self.cleaner(dry_run=dry_run).clean()
