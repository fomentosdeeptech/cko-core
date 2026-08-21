from __future__ import annotations

from pathlib import Path

import pytest

from cko_local_finder.application.discovery import run_discovery
from cko_local_finder.domain.models import DiscoveryPolicy
from cko_local_finder.infrastructure.filesystem import DiscoveryRootError, discover_files


def test_valid_root_and_supported_extensions(tmp_path: Path) -> None:
    for name in ("a.pdf", "b.docx", "c.txt", "d.md", "e.markdown", "UPPER.PDF"):
        (tmp_path / name).write_bytes(name.encode())
    files, issues, ignored = discover_files(tmp_path, DiscoveryPolicy())
    assert len(files) == 6 and issues == () and ignored == 0
    assert {item.extension for item in files} == {".pdf", ".docx", ".txt", ".md", ".markdown"}


@pytest.mark.parametrize("root", ["", "   ", None])
def test_root_must_be_explicit(root) -> None:
    with pytest.raises(DiscoveryRootError, match="explicitly"):
        discover_files(root, DiscoveryPolicy())


def test_missing_root_and_file_root_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(DiscoveryRootError, match="does not exist"):
        discover_files(tmp_path / "missing", DiscoveryPolicy())
    file_root = tmp_path / "file.txt"
    file_root.write_text("x", encoding="utf-8")
    with pytest.raises(DiscoveryRootError, match="directory"):
        discover_files(file_root, DiscoveryPolicy())


def test_unsupported_and_hidden_content_is_ignored(tmp_path: Path) -> None:
    (tmp_path / "visible.txt").write_text("visible", encoding="utf-8")
    (tmp_path / "unsupported.bin").write_bytes(b"binary")
    (tmp_path / ".hidden.txt").write_text("hidden", encoding="utf-8")
    hidden_dir = tmp_path / ".private"
    hidden_dir.mkdir()
    (hidden_dir / "nested.txt").write_text("hidden", encoding="utf-8")
    files, _, ignored = discover_files(tmp_path, DiscoveryPolicy())
    assert [item.relative_path for item in files] == ["visible.txt"]
    assert ignored == 3


def test_deterministic_order_relative_paths_and_confinement(tmp_path: Path) -> None:
    nested = tmp_path / "Folder"
    nested.mkdir()
    for name in ("z.txt", "B.txt", "a.txt"):
        (nested / name).write_text(name, encoding="utf-8")
    first = discover_files(tmp_path, DiscoveryPolicy())[0]
    second = discover_files(tmp_path, DiscoveryPolicy())[0]
    assert [item.relative_path for item in first] == ["Folder/a.txt", "Folder/B.txt", "Folder/z.txt"]
    assert first == second
    assert all(Path(item.absolute_path).is_relative_to(tmp_path.resolve()) for item in first)


def test_follow_symlinks_policy_is_explicitly_unsupported(tmp_path: Path) -> None:
    with pytest.raises(DiscoveryRootError, match="unsupported policy"):
        discover_files(tmp_path, DiscoveryPolicy(follow_symlinks=True))


def test_symlink_is_not_followed_and_escape_is_confined(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    link = root / "escape.txt"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation unsupported or not permitted: {exc}")
    files, issues, ignored = discover_files(root, DiscoveryPolicy())
    assert files == () and ignored == 1
    assert [(issue.path, issue.code) for issue in issues] == [("escape.txt", "symlink_ignored")]


def test_complete_synthetic_corpus(corpus_dir: Path, corpus) -> None:
    report = run_discovery(corpus_dir)
    assert report.discovered_count == 11
    assert report.ignored_count == 1
    assert report.duplicate_group_count == 1
    assert report.duplicate_groups[0].relative_paths == ("duplicates/copy.txt", "duplicates/original.txt")
    assert all(item.relative_path != "unsupported/sample.bin" for item in report.files)


def test_discovery_only_reads_bytes_for_hashing(tmp_path: Path) -> None:
    path = tmp_path / "opaque.pdf"
    payload = b"not a semantically valid PDF"
    path.write_bytes(payload)
    report = run_discovery(tmp_path)
    assert report.files[0].size_bytes == len(payload)
    assert path.read_bytes() == payload
