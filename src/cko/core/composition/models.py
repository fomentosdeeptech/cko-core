"""Public immutable models for the canonical CKO CORE composition root."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from cko.core.exceptions import CompositionError
from cko.core.storage.filesystem import FILESYSTEM_IDENTIFIER


@dataclass(frozen=True, slots=True)
class CoreCompositionSettings:
    """Declare infrastructure locations and composition policies."""

    workspace_root: str | Path | None = None
    filesystem_root: str | Path | None = None
    sqlite_database: str | Path | None = None
    checkpoint_storage_id: str = FILESYSTEM_IDENTIFIER
    sqlite_timeout: float = 5.0
    configure_logging: bool = True
    log_level: int | str = logging.INFO

    def __post_init__(self) -> None:
        if self.workspace_root is not None and not isinstance(
            self.workspace_root, (str, Path)
        ):
            raise CompositionError("workspace_root must be a path")
        if self.filesystem_root is not None and not isinstance(
            self.filesystem_root, (str, Path)
        ):
            raise CompositionError("filesystem_root must be a path")
        if self.sqlite_database is not None and not isinstance(
            self.sqlite_database, (str, Path)
        ):
            raise CompositionError("sqlite_database must be a path")
        if (
            not isinstance(self.checkpoint_storage_id, str)
            or not self.checkpoint_storage_id.strip()
        ):
            raise CompositionError(
                "checkpoint_storage_id must be a non-empty string"
            )
        object.__setattr__(
            self,
            "checkpoint_storage_id",
            self.checkpoint_storage_id.strip(),
        )
        if (
            isinstance(self.sqlite_timeout, bool)
            or not isinstance(self.sqlite_timeout, (int, float))
            or self.sqlite_timeout <= 0
        ):
            raise CompositionError("sqlite_timeout must be a positive number")
        object.__setattr__(self, "sqlite_timeout", float(self.sqlite_timeout))
        if not isinstance(self.configure_logging, bool):
            raise CompositionError("configure_logging must be boolean")
        if not isinstance(self.log_level, (int, str)):
            raise CompositionError("log_level must be an integer or string")


__all__ = ["CoreCompositionSettings"]
