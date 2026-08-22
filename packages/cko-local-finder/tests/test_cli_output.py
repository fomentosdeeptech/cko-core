from __future__ import annotations
from io import StringIO
import json
from pathlib import Path
import sqlite3
import pytest
from cko_local_finder.cli import runtime
from cko_local_finder.cli.main import build_parser, main
from cko_local_finder.cli.presenters import json_output
from cko_local_finder.infrastructure.sqlite import RepositoryError, SQLiteDocumentRepository

def invoke(*args: str):
    stdout, stderr = StringIO(), StringIO()
    code = main(args, stdout=stdout, stderr=stderr)
    return code, stdout.getvalue(), stderr.getvalue()

@pytest.fixture
def ingested(tmp_path: Path):
    root = tmp_path / "corpus"; root.mkdir()
    (root / "regulamento.txt").write_text("inovação café conhecimento", encoding="utf-8")
    (root / "cópia.txt").write_text("inovação café conhecimento", encoding="utf-8")
    (root / "nota.md").write_text("# Evidência\ntermo exclusivo", encoding="utf-8")
    database = tmp_path / "finder.db"
    code, stdout, stderr = invoke("ingest", str(root), "--database", str(database), "--format", "json")
    assert code == 0 and not stderr
    return root, database, json.loads(stdout)

def test_parser_help_version_and_all_commands():
    assert build_parser().prog == "cko-local-finder"
    for args in (("--help",), ("--version",), ("ingest", "--help"), ("search", "--help"),
                 ("show", "--help"), ("duplicates", "--help"), ("report", "--help")):
        code, stdout, stderr = invoke(*args)
        assert code == 0 and stdout and not stderr

@pytest.mark.parametrize("args", [(), ("ingest",), ("search", "x"), ("show", "a" * 64),
                                  ("duplicates",), ("report", "failures")])
def test_required_arguments_use_exit_two(args):
    code, stdout, stderr = invoke(*args)
    assert code == 2 and not stdout and "traceback" not in stderr.lower()

def test_invalid_limit_and_report_type_use_exit_two():
    assert invoke("search", "x", "--database", "x", "--limit", "101")[0] == 2
    assert invoke("report", "unknown", "--database", "x")[0] == 2

def test_ingest_search_show_duplicates_and_reports(ingested):
    root, database, payload = ingested
    assert payload["discovered_documents"] == 3 and payload["duplicate_groups"] == 1
    code, stdout, stderr = invoke("search", "café", "--database", str(database), "--extension", "txt", "--format", "json")
    search = json.loads(stdout); assert code == 0 and not stderr and search["total_matches"] == 1
    assert all("[[" in item["snippet"] and "]]" in item["snippet"] for item in search["results"])
    digest = search["results"][0]["sha256"]
    code, stdout, stderr = invoke("show", digest, "--database", str(database), "--format", "json")
    shown = json.loads(stdout); assert code == 0 and not stderr and len(shown["document"]["origins"]) == 2
    code, stdout, _ = invoke("duplicates", "--database", str(database), "--format", "json")
    assert code == 0 and len(json.loads(stdout)["duplicates"]) == 1
    for report_type in ("ingestion", "failures", "duplicates"):
        args = ["report", report_type, "--database", str(database), "--format", "json"]
        if report_type == "ingestion": args.extend(("--root", str(root.resolve())))
        code, stdout, stderr = invoke(*args); assert code == 0 and json.loads(stdout) is not None and not stderr

def test_search_no_results_and_empty_duplicates_are_success(tmp_path: Path):
    root = tmp_path / "root"; root.mkdir(); (root / "one.txt").write_text("alpha", encoding="utf-8")
    database = tmp_path / "db.sqlite"; assert invoke("ingest", str(root), "--database", str(database))[0] == 0
    assert json.loads(invoke("search", "missing", "--database", str(database), "--format", "json")[1])["results"] == []
    assert json.loads(invoke("duplicates", "--database", str(database), "--format", "json")[1])["duplicates"] == []

def test_ingestion_is_idempotent(ingested):
    root, database, _ = ingested
    first = invoke("ingest", str(root), "--database", str(database), "--format", "json")
    second = invoke("ingest", str(root), "--database", str(database), "--format", "json")
    assert first[0] == second[0] == 0
    assert json.loads(first[1])["unique_documents"] == json.loads(second[1])["unique_documents"] == 2

def test_isolated_extraction_failure_returns_one(tmp_path: Path):
    root = tmp_path / "root"; root.mkdir()
    (root / "good.txt").write_text("searchable", encoding="utf-8")
    (root / "bad.txt").write_bytes(b"\xff\xfe\x00")
    database = tmp_path / "db.sqlite"
    code, stdout, stderr = invoke("ingest", str(root), "--database", str(database), "--format", "json")
    assert code == 1 and not stderr and json.loads(stdout)["recoverable_failures"] == 1
    assert json.loads(invoke("search", "searchable", "--database", str(database), "--format", "json")[1])["total_matches"] == 1

def test_text_json_unicode_newline_and_no_ansi(ingested):
    _, database, _ = ingested
    code, text, stderr = invoke("search", "café", "--database", str(database))
    assert code == 0 and text.endswith("\n") and "\x1b[" not in text and not stderr
    value = {"z": "café", "a": 1}
    assert json_output(value) == json_output(value) == '{"a":1,"z":"café"}\n'

def test_safe_not_found_and_invalid_hash(tmp_path: Path):
    code, stdout, stderr = invoke("search", "x", "--database", str(tmp_path / "missing.db"))
    assert code == 3 and not stdout and "traceback" not in stderr.lower() and "select " not in stderr.lower()
    database = tmp_path / "db.sqlite"; SQLiteDocumentRepository(database).apply_provenance_migrations()
    assert invoke("show", "not-a-hash", "--database", str(database))[0] == 2
    assert invoke("show", "a" * 64, "--database", str(database))[0] == 3

def test_database_resource_and_internal_exit_codes(monkeypatch, tmp_path: Path):
    database = tmp_path / "db.sqlite"; database.touch()
    monkeypatch.setattr(runtime, "_repository", lambda *a, **k: (_ for _ in ()).throw(RepositoryError("SELECT secret")))
    code, _, stderr = invoke("search", "x", "--database", str(database)); assert code == 4 and "SELECT" not in stderr
    monkeypatch.setattr(runtime, "_repository", lambda *a, **k: (_ for _ in ()).throw(runtime.RequiredResourceUnavailable("FTS5 is unavailable")))
    assert invoke("search", "x", "--database", str(database))[0] == 5
    monkeypatch.setattr(runtime, "_repository", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("secret")))
    code, _, stderr = invoke("search", "x", "--database", str(database)); assert code == 10 and "secret" not in stderr
