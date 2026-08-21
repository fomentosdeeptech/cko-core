from __future__ import annotations

import hashlib
import io
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from cko_local_finder.infrastructure.hashing import HashingError, hash_file


@pytest.mark.parametrize("payload", [b"", b"synthetic text", bytes(range(256)) * 20])
def test_hash_matches_hashlib(tmp_path: Path, payload: bytes) -> None:
    path = tmp_path / "document.txt"
    path.write_bytes(payload)
    assert hash_file(path, chunk_size=17) == hashlib.sha256(payload).hexdigest()


def test_multiple_blocks_and_determinism(tmp_path: Path) -> None:
    path = tmp_path / "blocks.bin"
    path.write_bytes(b"abc" * 100)
    first = hash_file(path, chunk_size=7)
    assert first == hash_file(path, chunk_size=11)
    assert len(first) == 64 and first == first.lower()


@pytest.mark.parametrize("chunk_size", [0, -1])
def test_invalid_chunk_size(tmp_path: Path, chunk_size: int) -> None:
    with pytest.raises(ValueError, match="positive"):
        hash_file(tmp_path / "unused", chunk_size)


def test_missing_file_has_sanitized_error(tmp_path: Path) -> None:
    with pytest.raises(HashingError, match="could not be read") as captured:
        hash_file(tmp_path / "missing.txt")
    assert captured.value.code == "hash_read_error"
    assert str(tmp_path) not in str(captured.value)


def test_mutation_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "changing.txt"
    path.write_bytes(b"stable bytes")
    before = SimpleNamespace(st_size=12, st_mtime_ns=1)
    after = SimpleNamespace(st_size=13, st_mtime_ns=2)
    with patch.object(Path, "stat", side_effect=[before, after]):
        with pytest.raises(HashingError) as captured:
            hash_file(path, opener=lambda _: io.BytesIO(b"stable bytes"))
    assert captured.value.code == "file_changed_during_hash"


def test_hashing_does_not_write_or_change_metadata(tmp_path: Path) -> None:
    path = tmp_path / "readonly.txt"
    path.write_bytes(b"read only")
    before = path.stat()
    hash_file(path)
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)


def test_unreadable_when_reproducible(tmp_path: Path) -> None:
    path = tmp_path / "denied.txt"
    path.write_bytes(b"content")
    def denied(_: Path):
        raise PermissionError("denied")
    with pytest.raises(HashingError) as captured:
        hash_file(path, opener=denied)
    assert captured.value.code == "hash_read_error"
