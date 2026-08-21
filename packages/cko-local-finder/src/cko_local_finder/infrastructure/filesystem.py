"""Confined and deterministic local filesystem discovery adapter."""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path

from cko_local_finder.domain.models import DiscoveryIssue, DiscoveryPolicy, DiscoveredFile
from cko_local_finder.infrastructure.hashing import HashingError, hash_file


class DiscoveryRootError(ValueError):
    """Fatal validation error for the explicitly supplied discovery root."""


def _hidden(path: Path) -> bool:
    if path.name.startswith("."):
        return True
    try:
        return bool(getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0) & 2)
    except OSError:
        return False


def _safe_issue(path: str, stage: str, code: str, message: str) -> DiscoveryIssue:
    return DiscoveryIssue(path or ".", stage, code, message, True)


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def discover_files(
    root: str | Path,
    policy: DiscoveryPolicy,
) -> tuple[tuple[DiscoveredFile, ...], tuple[DiscoveryIssue, ...], int]:
    """Discover supported regular files without modifying or semantically reading them."""
    if not isinstance(root, (str, Path)) or not str(root).strip():
        raise DiscoveryRootError("root must be explicitly provided")
    requested = Path(root).expanduser()
    try:
        normalized = requested.resolve(strict=True)
    except OSError as exc:
        raise DiscoveryRootError("root does not exist or cannot be resolved") from exc
    if not normalized.is_dir():
        raise DiscoveryRootError("root must be a directory")
    if policy.follow_symlinks:
        raise DiscoveryRootError("unsupported policy: following symlinks is not implemented")

    found: list[DiscoveredFile] = []
    issues: list[DiscoveryIssue] = []
    ignored = 0
    pending = [normalized]
    while pending:
        directory = pending.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: (item.name.casefold(), item.name))
        except OSError:
            relative = "." if directory == normalized else _relative(directory, normalized)
            issues.append(_safe_issue(relative, "enumerate", "directory_read_error", "directory could not be enumerated"))
            continue
        child_directories: list[Path] = []
        for entry in entries:
            path = Path(entry.path)
            relative_hint = _relative(path, normalized)
            try:
                if entry.is_symlink():
                    ignored += 1
                    issues.append(_safe_issue(relative_hint, "policy", "symlink_ignored", "symbolic link was not followed"))
                    continue
                if policy.ignore_hidden and _hidden(path):
                    ignored += 1
                    continue
                if entry.is_dir(follow_symlinks=False):
                    child_directories.append(path)
                    continue
                if not entry.is_file(follow_symlinks=False):
                    ignored += 1
                    continue
                extension = path.suffix.lower()
                if extension not in policy.supported_extensions:
                    ignored += 1
                    continue
                resolved = path.resolve(strict=True)
                if not resolved.is_relative_to(normalized):
                    ignored += 1
                    issues.append(_safe_issue(relative_hint, "confinement", "path_escape", "candidate resolved outside the authorized root"))
                    continue
                before = resolved.stat()
                digest = hash_file(resolved, policy.hash_chunk_size)
                after = resolved.stat()
                if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                    raise HashingError("file_changed_during_discovery", "file changed while metadata was observed")
                relative = _relative(resolved, normalized)
                media_type = mimetypes.guess_type(resolved.name)[0] or "application/octet-stream"
                found.append(DiscoveredFile(
                    digest, str(resolved), relative, digest, after.st_size,
                    extension, after.st_mtime_ns, media_type, False,
                ))
            except HashingError as exc:
                issues.append(_safe_issue(relative_hint, "hash", exc.code, str(exc)))
            except OSError:
                issues.append(_safe_issue(relative_hint, "metadata", "file_access_error", "file metadata or content could not be read"))
        pending.extend(reversed(child_directories))
    found.sort(key=lambda item: (item.relative_path.casefold(), item.relative_path))
    issues.sort(key=lambda item: (item.path.casefold(), item.path, item.stage, item.code))
    return tuple(found), tuple(issues), ignored
