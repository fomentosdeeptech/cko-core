"""Application orchestration for safe in-memory local discovery."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from cko_local_finder.application.duplicates import group_duplicates
from cko_local_finder.domain.models import DiscoveryIssue, DiscoveryPolicy, DiscoveryReport, DiscoveredFile
from cko_local_finder.infrastructure.filesystem import discover_files

Scanner = Callable[[str | Path, DiscoveryPolicy], tuple[tuple[DiscoveredFile, ...], tuple[DiscoveryIssue, ...], int]]


def run_discovery(
    root: str | Path,
    policy: DiscoveryPolicy | None = None,
    *,
    scanner: Scanner = discover_files,
) -> DiscoveryReport:
    """Coordinate scanning and duplicate grouping without persistence or output."""
    effective_policy = policy or DiscoveryPolicy()
    files, issues, ignored_count = scanner(root, effective_policy)
    ordered_files = tuple(sorted(files, key=lambda item: (item.relative_path.casefold(), item.relative_path)))
    ordered_issues = tuple(sorted(issues, key=lambda item: (item.path.casefold(), item.path, item.stage, item.code)))
    duplicates = group_duplicates(ordered_files)
    normalized_root = str(Path(root).expanduser().resolve(strict=True))
    return DiscoveryReport(
        normalized_root, ordered_files, duplicates, ignored_count, ordered_issues,
        len(ordered_files), len(duplicates), len(ordered_issues),
    )
