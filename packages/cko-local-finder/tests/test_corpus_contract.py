from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re


def test_manifest_schema_and_unique_identity(expected_manifest) -> None:
    assert expected_manifest["schema_version"] == 1
    cases = expected_manifest["cases"]
    assert len(cases) == 12
    assert len({case["id"] for case in cases}) == len(cases)
    assert len({case["path"] for case in cases}) == len(cases)
    required = {"id", "path", "family", "condition", "duplicate", "encoding", "structurally_valid", "purpose"}
    assert all(set(case) == required for case in cases)


def test_manifest_paths_are_relative_and_confined(expected_manifest) -> None:
    for case in expected_manifest["cases"]:
        path = PurePosixPath(case["path"])
        assert not path.is_absolute()
        assert ".." not in path.parts
        assert "\\" not in case["path"]


def test_manifest_matches_materialized_cases(expected_manifest, corpus) -> None:
    expected = {case["path"]: case["condition"] for case in expected_manifest["cases"]}
    actual = {item["path"]: item["case_type"] for item in corpus}
    assert actual == expected


def test_required_formats_and_edge_conditions(expected_manifest) -> None:
    families = {case["family"] for case in expected_manifest["cases"]}
    conditions = {case["condition"] for case in expected_manifest["cases"]}
    assert {"pdf", "docx", "txt", "markdown"} <= families
    assert {"empty", "corrupt", "unsupported", "duplicate", "oversized"} <= conditions
    duplicate_cases = [case for case in expected_manifest["cases"] if case["duplicate"]]
    assert len(duplicate_cases) == 2


def test_sha256_is_canonical_and_deterministic(corpus_dir: Path, corpus) -> None:
    for item in corpus:
        digest = hashlib.sha256((corpus_dir / item["path"]).read_bytes()).hexdigest()
        assert re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
        assert item["sha256"] == digest


def test_sources_have_exactly_one_final_newline() -> None:
    source_root = Path(__file__).parent / "fixtures" / "source"
    for path in source_root.iterdir():
        payload = path.read_bytes()
        assert payload.endswith(b"\n")
        assert not payload.endswith(b"\n\n")
        payload.decode("utf-8")


def test_corpus_contains_no_personal_data(expected_manifest, corpus_dir: Path, corpus) -> None:
    manifest_text = json.dumps(expected_manifest, ensure_ascii=False)
    textual = [manifest_text]
    for item in corpus:
        path = corpus_dir / item["path"]
        if path.suffix in {".txt", ".md"}:
            textual.append(path.read_text(encoding="utf-8-sig"))
    combined = "\n".join(textual)
    assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", combined)
    assert not re.search(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", combined)
    assert not re.search(r"\b(?:\d[ .-]?){13,16}\b", combined)
