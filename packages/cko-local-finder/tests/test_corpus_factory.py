from __future__ import annotations

import hashlib
from pathlib import Path
import zipfile

from .corpus_factory import ZIP_TIMESTAMP, materialize_corpus


EXPECTED_PATHS = {
    "valid/sample_utf8.txt", "valid/sample_utf8_sig.txt", "valid/sample.md",
    "valid/sample.pdf", "valid/sample.docx", "edge/empty.txt",
    "edge/oversized.txt", "corrupt/corrupt.pdf", "corrupt/corrupt.docx",
    "unsupported/sample.bin", "duplicates/original.txt", "duplicates/copy.txt",
}


def _bytes_by_path(root: Path, manifest: list[dict[str, object]]) -> dict[str, bytes]:
    return {str(item["path"]): (root / str(item["path"])).read_bytes() for item in manifest}


def test_creates_every_expected_case(corpus_dir: Path, corpus: list[dict[str, object]]) -> None:
    assert {str(item["path"]) for item in corpus} == EXPECTED_PATHS
    assert all((corpus_dir / str(item["path"])).is_file() for item in corpus)


def test_materializations_are_byte_deterministic(tmp_path: Path, test_size_limit: int) -> None:
    first_root, second_root = tmp_path / "first", tmp_path / "second"
    first = materialize_corpus(first_root, size_limit=test_size_limit)
    second = materialize_corpus(second_root, size_limit=test_size_limit)
    assert first == second
    assert _bytes_by_path(first_root, first) == _bytes_by_path(second_root, second)


def test_hashes_match_bytes(corpus_dir: Path, corpus: list[dict[str, object]]) -> None:
    for item in corpus:
        payload = (corpus_dir / str(item["path"])).read_bytes()
        assert item["sha256"] == hashlib.sha256(payload).hexdigest()


def test_duplicate_pair_and_unique_cases(corpus_dir: Path, corpus: list[dict[str, object]]) -> None:
    payloads = _bytes_by_path(corpus_dir, corpus)
    assert payloads["duplicates/original.txt"] == payloads["duplicates/copy.txt"]
    nonduplicates = [data for path, data in payloads.items() if not path.startswith("duplicates/")]
    assert len(nonduplicates) == len(set(nonduplicates))


def test_minimal_pdf_structure(corpus_dir: Path, corpus) -> None:
    payload = (corpus_dir / "valid/sample.pdf").read_bytes()
    assert payload.startswith(b"%PDF-1.4")
    assert b"Synthetic local knowledge corpus" in payload
    assert b"xref\n" in payload and payload.endswith(b"%%EOF\n")


def test_docx_zip_structure_and_timestamps(corpus_dir: Path, corpus) -> None:
    with zipfile.ZipFile(corpus_dir / "valid/sample.docx") as archive:
        assert archive.testzip() is None
        assert archive.namelist() == sorted(archive.namelist())
        assert set(archive.namelist()) == {"[Content_Types].xml", "_rels/.rels", "word/document.xml"}
        assert all(info.date_time == ZIP_TIMESTAMP for info in archive.infolist())


def test_corrupt_files_are_not_valid_containers(corpus_dir: Path, corpus) -> None:
    assert not (corpus_dir / "corrupt/corrupt.pdf").read_bytes().endswith(b"%%EOF\n")
    assert not zipfile.is_zipfile(corpus_dir / "corrupt/corrupt.docx")
    assert zipfile.is_zipfile(corpus_dir / "valid/sample.docx")


def test_oversized_uses_configurable_small_limit(tmp_path: Path) -> None:
    root = tmp_path / "sized"
    materialize_corpus(root, size_limit=7)
    assert (root / "edge/oversized.txt").stat().st_size == 8


def test_utf8_and_utf8_sig(corpus_dir: Path, corpus) -> None:
    plain = (corpus_dir / "valid/sample_utf8.txt").read_bytes()
    signed = (corpus_dir / "valid/sample_utf8_sig.txt").read_bytes()
    assert not plain.startswith(b"\xef\xbb\xbf")
    assert signed == b"\xef\xbb\xbf" + plain
    assert "acentuação" in plain.decode("utf-8")
    assert signed.decode("utf-8-sig") == plain.decode("utf-8")


def test_no_writes_outside_explicit_root(tmp_path: Path) -> None:
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("unchanged\n", encoding="utf-8")
    before = sentinel.read_bytes()
    root = tmp_path / "only-here"
    materialize_corpus(root)
    assert sentinel.read_bytes() == before
    assert {path.name for path in tmp_path.iterdir()} == {"sentinel.txt", "only-here"}


def test_safe_symlink_fixture(safe_symlink: tuple[Path, Path]) -> None:
    target, link = safe_symlink
    assert link.is_symlink()
    assert link.read_bytes() == target.read_bytes()
