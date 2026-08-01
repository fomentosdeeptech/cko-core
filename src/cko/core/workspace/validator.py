"""Environment validation for the supported local development platform."""

from __future__ import annotations

import locale
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Callable

from .manager import WorkspaceManager


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ValidationCheck:
    """Result of one environment requirement check."""

    name: str
    passed: bool
    value: str
    requirement: str


@dataclass(frozen=True, slots=True)
class EnvironmentValidationResult:
    """Complete immutable environment validation report."""

    checks: tuple[ValidationCheck, ...]

    @property
    def valid(self) -> bool:
        """Return ``True`` only when every check passed."""
        return all(item.passed for item in self.checks)


class EnvironmentValidator:
    """Validate versions, permissions, UTF-8 and available disk space."""

    def __init__(
        self,
        manager: WorkspaceManager,
        *,
        minimum_free_bytes: int = 100 * 1024 * 1024,
        powershell_version: Callable[[], tuple[int, ...]] | None = None,
    ) -> None:
        if minimum_free_bytes < 0:
            raise ValueError("minimum_free_bytes must be non-negative")
        self.manager = manager
        self.minimum_free_bytes = minimum_free_bytes
        self._powershell_version = powershell_version or self._read_powershell_version

    @staticmethod
    def _read_powershell_version() -> tuple[int, ...]:
        executable = shutil.which("powershell.exe") or shutil.which("powershell")
        if executable is None:
            return ()
        try:
            completed = subprocess.run(
                [
                    executable,
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    "$PSVersionTable.PSVersion.ToString()",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
            )
        except (OSError, subprocess.SubprocessError):
            return ()
        value = completed.stdout.strip().split(".")
        try:
            return tuple(int(part) for part in value)
        except ValueError:
            return ()

    @staticmethod
    def _is_utf8(value: str | None) -> bool:
        normalized = (value or "").lower().replace("-", "").replace("_", "")
        return normalized in {"utf8", "utf8sig"}

    def validate(self) -> EnvironmentValidationResult:
        """Run all supported environment checks and emit an audit event."""
        self.manager.create()
        python_version = sys.version_info[:3]
        powershell_version = self._powershell_version()
        encoding_values = {
            sys.getfilesystemencoding(),
            locale.getpreferredencoding(False),
            sys.stdout.encoding,
        }
        encoding_values.discard(None)
        free_bytes = shutil.disk_usage(self.manager.paths.root).free
        checks = (
            ValidationCheck(
                "python", python_version >= (3, 13),
                ".".join(map(str, python_version)), ">=3.13",
            ),
            ValidationCheck(
                "powershell", powershell_version >= (5, 1),
                ".".join(map(str, powershell_version)) or "not found", ">=5.1",
            ),
            ValidationCheck(
                "permissions", self.manager.validate_permissions(),
                "write/delete probe", "writable runtime/temp",
            ),
            ValidationCheck(
                "encoding", all(self._is_utf8(item) for item in encoding_values),
                ", ".join(sorted(encoding_values)), "UTF-8",
            ),
            ValidationCheck(
                "disk_space", free_bytes >= self.minimum_free_bytes,
                str(free_bytes), f">={self.minimum_free_bytes} bytes",
            ),
        )
        result = EnvironmentValidationResult(checks)
        LOGGER.info(
            "validation completed",
            extra={
                "event": "validation_completed",
                "context": {
                    "valid": result.valid,
                    "checks": {
                        item.name: item.passed for item in result.checks
                    },
                },
            },
        )
        return result
