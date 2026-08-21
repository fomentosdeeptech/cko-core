from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from cko_local_finder.application.discovery import run_discovery
from cko_local_finder.domain.models import DiscoveryPolicy
from cko_local_finder.infrastructure import filesystem
from cko_local_finder.infrastructure.filesystem import DiscoveryRootError, discover_files
from cko_local_finder.infrastructure.hashing import HashingError


def test_isolated_hash_failure_does_not_stop_batch(tmp_path: Path) -> None:
    good = tmp_path / "good.txt"
    bad = tmp_path / "bad.txt"
    good.write_text("good", encoding="utf-8")
    bad.write_text("bad", encoding="utf-8")
    original = filesystem.hash_file
    def selective(path: Path, chunk_size: int):
        if path.name == "bad.txt":
            raise HashingError("hash_read_error", "file could not be read for hashing")
        return original(path, chunk_size)
    with patch.object(filesystem, "hash_file", side_effect=selective):
        files, issues, _ = discover_files(tmp_path, DiscoveryPolicy())
    assert [item.relative_path for item in files] == ["good.txt"]
    assert issues[0].path == "bad.txt" and issues[0].recoverable


def test_removed_file_becomes_sanitized_issue(tmp_path: Path) -> None:
    path = tmp_path / "removed.txt"
    path.write_text("temporary", encoding="utf-8")
    def remove_then_fail(candidate: Path, chunk_size: int):
        candidate.unlink()
        raise HashingError("hash_read_error", "file could not be read for hashing")
    with patch.object(filesystem, "hash_file", side_effect=remove_then_fail):
        files, issues, _ = discover_files(tmp_path, DiscoveryPolicy())
    assert files == () and issues[0].code == "hash_read_error"
    assert str(tmp_path) not in issues[0].message


def test_changed_file_issue_is_recoverable(tmp_path: Path) -> None:
    path = tmp_path / "changing.txt"
    path.write_text("content", encoding="utf-8")
    with patch.object(filesystem, "hash_file", side_effect=HashingError("file_changed_during_hash", "file changed while its identity was calculated")):
        _, issues, _ = discover_files(tmp_path, DiscoveryPolicy())
    assert issues[0].code == "file_changed_during_hash" and issues[0].recoverable


def test_permission_denied_is_sanitized_when_reproducible(tmp_path: Path) -> None:
    path = tmp_path / "denied.txt"
    path.write_text("content", encoding="utf-8")
    with patch.object(filesystem, "hash_file", side_effect=HashingError("hash_read_error", "file could not be read for hashing")):
        _, issues, _ = discover_files(tmp_path, DiscoveryPolicy())
    assert issues[0].message == "file could not be read for hashing"


def test_invalid_root_stops_before_scanning(tmp_path: Path) -> None:
    with pytest.raises(DiscoveryRootError):
        run_discovery(tmp_path / "missing")


def test_no_write_outside_explicit_temporary_root(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "file.txt").write_text("content", encoding="utf-8")
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("unchanged", encoding="utf-8")
    before = {item.name: item.read_bytes() for item in tmp_path.iterdir() if item.is_file()}
    run_discovery(root)
    after = {item.name: item.read_bytes() for item in tmp_path.iterdir() if item.is_file()}
    assert before == after
