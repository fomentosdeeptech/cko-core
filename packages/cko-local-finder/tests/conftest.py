from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from .corpus_factory import DEFAULT_TEST_SIZE_LIMIT, materialize_corpus


@pytest.fixture
def test_size_limit() -> int:
    return DEFAULT_TEST_SIZE_LIMIT


@pytest.fixture
def corpus_dir(tmp_path: Path) -> Path:
    return tmp_path / "corpus"


@pytest.fixture
def corpus(corpus_dir: Path, test_size_limit: int) -> list[dict[str, object]]:
    return materialize_corpus(corpus_dir, size_limit=test_size_limit)


@pytest.fixture
def expected_manifest() -> dict[str, object]:
    path = Path(__file__).parent / "fixtures" / "corpus_manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def safe_symlink(tmp_path: Path) -> tuple[Path, Path]:
    target = tmp_path / "target.txt"
    link = tmp_path / "target-link.txt"
    target.write_text("synthetic symlink target\n", encoding="utf-8")
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation unsupported or not permitted: {exc}")
    return target, link
