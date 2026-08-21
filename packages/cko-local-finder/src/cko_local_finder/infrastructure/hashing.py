"""Incremental, read-only SHA-256 hashing with mutation detection."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import BinaryIO, Callable

DEFAULT_CHUNK_SIZE = 1024 * 1024


class HashingError(OSError):
    """Sanitized hashing failure carrying a stable issue code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def hash_file(
    path: str | Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    *,
    opener: Callable[[Path], BinaryIO] | None = None,
) -> str:
    """Return a lowercase SHA-256 after stable pre/post metadata checks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    candidate = Path(path)
    try:
        before = candidate.stat()
        digest = hashlib.sha256()
        open_binary = opener or (lambda item: item.open("rb"))
        with open_binary(candidate) as stream:
            while chunk := stream.read(chunk_size):
                digest.update(chunk)
        after = candidate.stat()
    except HashingError:
        raise
    except OSError as exc:
        raise HashingError("hash_read_error", "file could not be read for hashing") from exc
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise HashingError("file_changed_during_hash", "file changed while its identity was calculated")
    return digest.hexdigest()
