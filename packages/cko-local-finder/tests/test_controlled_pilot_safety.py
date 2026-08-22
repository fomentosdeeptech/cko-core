from __future__ import annotations

from io import StringIO
import os
from pathlib import Path

import pytest

from cko_local_finder.cli.main import main
from cko_local_finder.domain.models import DiscoveryPolicy, ExtractionPolicy
from cko_local_finder.infrastructure.filesystem import discover_files


def invoke(*args: str) -> tuple[int, str, str]:
    stdout, stderr = StringIO(), StringIO()
    code = main(args, stdout=stdout, stderr=stderr)
    return code, stdout.getvalue(), stderr.getvalue()


def test_default_hidden_and_unsupported_files_are_ignored(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "visible.txt").write_text("visible", encoding="utf-8")
    (root / ".hidden.txt").write_text("hidden", encoding="utf-8")
    (root / "unsupported.bin").write_bytes(b"synthetic")
    files, issues, ignored = discover_files(root, DiscoveryPolicy())
    assert [item.relative_path for item in files] == ["visible.txt"]
    assert issues == () and ignored == 2


def test_symlink_escape_is_not_followed_by_default(tmp_path: Path) -> None:
    root, outside = tmp_path / "root", tmp_path / "outside"
    root.mkdir(); outside.mkdir()
    target = outside / "secret.txt"
    target.write_text("synthetic outside", encoding="utf-8")
    link = root / "escape.txt"
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation unsupported or not permitted: {exc}")
    report = discover_files(root, DiscoveryPolicy(follow_symlinks=False))
    assert report.files == () and report.ignored_count == 1


def test_follow_symlinks_request_fails_closed(tmp_path: Path) -> None:
    root = tmp_path / "root"; root.mkdir()
    code, stdout, stderr = invoke(
        "ingest", str(root), "--database", str(tmp_path / "finder.sqlite"), "--follow-symlinks"
    )
    assert code == 2 and not stdout and "unsupported policy" in stderr.lower()


def test_size_and_query_result_limits_are_enforced(tmp_path: Path) -> None:
    policy = ExtractionPolicy()
    assert policy.max_source_file_size == 50 * 1024 * 1024
    database = tmp_path / "finder.sqlite"
    root = tmp_path / "root"; root.mkdir()
    (root / "small.txt").write_text("synthetic", encoding="utf-8")
    assert invoke("ingest", str(root), "--database", str(database))[0] == 0
    assert invoke("search", "synthetic", "--database", str(database), "--limit", "0")[0] == 2
    assert invoke("search", "synthetic", "--database", str(database), "--limit", "101")[0] == 2


def test_failures_are_sanitized_and_recoverable(tmp_path: Path) -> None:
    root = tmp_path / "root"; root.mkdir()
    (root / "good.txt").write_text("recoverable searchable", encoding="utf-8")
    (root / "bad.txt").write_bytes(b"\xff\xfe\x00")
    database = tmp_path / "finder.sqlite"
    code, stdout, stderr = invoke("ingest", str(root), "--database", str(database), "--format", "json")
    assert code == 1 and not stderr and "traceback" not in stdout.lower() and "select " not in stdout.lower()
    code, stdout, stderr = invoke("search", "searchable", "--database", str(database), "--format", "json")
    assert code == 0 and '"total_matches":1' in stdout and not stderr
