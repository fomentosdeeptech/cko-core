from __future__ import annotations

from cko_local_finder.application.duplicates import group_duplicates
from cko_local_finder.domain.models import DiscoveredFile


def _file(path: str, digest: str, size: int = 4) -> DiscoveredFile:
    return DiscoveredFile(digest, f"/synthetic/{path}", path, digest, size, ".txt", 1, "text/plain")


def test_no_duplicates() -> None:
    assert group_duplicates((_file("a.txt", "a" * 64), _file("b.txt", "b" * 64))) == ()


def test_pair_preserves_both_locations() -> None:
    groups = group_duplicates((_file("z.txt", "a" * 64), _file("a.txt", "a" * 64)))
    assert groups[0].relative_paths == ("a.txt", "z.txt")


def test_three_locations_are_preserved() -> None:
    files = tuple(_file(path, "c" * 64) for path in ("c.txt", "a.txt", "b.txt"))
    assert group_duplicates(files)[0].relative_paths == ("a.txt", "b.txt", "c.txt")


def test_same_name_or_size_does_not_prove_duplicate() -> None:
    files = (_file("one/same.txt", "a" * 64), _file("two/same.txt", "b" * 64))
    assert group_duplicates(files) == ()


def test_groups_are_hash_sorted_and_input_is_unchanged() -> None:
    files = [
        _file("z2.txt", "f" * 64), _file("z1.txt", "f" * 64),
        _file("a2.txt", "1" * 64), _file("a1.txt", "1" * 64),
    ]
    snapshot = list(files)
    groups = group_duplicates(files)
    assert [group.sha256 for group in groups] == ["1" * 64, "f" * 64]
    assert files == snapshot


def test_inconsistent_size_for_same_hash_is_rejected() -> None:
    try:
        group_duplicates((_file("a.txt", "d" * 64, 1), _file("b.txt", "d" * 64, 2)))
    except ValueError as exc:
        assert "consistent size" in str(exc)
    else:
        raise AssertionError("inconsistent physical identity was accepted")
