from __future__ import annotations

import ast
from pathlib import Path
import sqlite3
import tomllib

import cko_local_finder
from cko_local_finder.domain.models import ExtractionPolicy, SearchFilter, SearchQuery
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository


PACKAGE_ROOT = Path(__file__).parents[1]
PRODUCTION_ROOT = PACKAGE_ROOT / "src" / "cko_local_finder"


def test_permanent_readiness_gates() -> None:
    project = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert cko_local_finder.__version__ == project["version"] == "0.1.0"
    assert cko_local_finder.__all__ == ("__version__",)
    assert len(project["dependencies"]) == 2
    assert ExtractionPolicy().max_source_file_size == 50 * 1024 * 1024


def test_sqlite_schema_fts5_and_parameterized_search(tmp_path: Path) -> None:
    repository = SQLiteDocumentRepository(tmp_path / "readiness.sqlite")
    assert repository.apply_provenance_migrations() == 3
    capability = repository.capabilities()
    assert capability.schema_version == 3 and capability.fts5_available and capability.foreign_keys_enabled
    query = SearchQuery("term' OR 1=1 --", SearchFilter(path_prefix="safe/"), limit=1)
    assert repository.search(query).total_matches == 0


def test_no_network_telemetry_ocr_macro_or_core_dependency() -> None:
    forbidden_imports = {"requests", "httpx", "urllib", "socket", "pytesseract", "cko", "cko_fcp"}
    forbidden_calls = {"urlopen", "request", "post", "get", "ocr", "run_macro", "exec", "eval"}
    for path in sorted(PRODUCTION_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not ({alias.name.split(".")[0] for alias in node.names} & forbidden_imports)
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden_imports
            elif isinstance(node, ast.Call):
                name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                assert name not in forbidden_calls


def test_source_tree_has_no_embedded_database_build_or_report_outputs() -> None:
    forbidden_suffixes = {".db", ".sqlite", ".sqlite3", ".whl"}
    assert not [path for path in PACKAGE_ROOT.rglob("*") if path.is_file() and path.suffix.lower() in forbidden_suffixes]
    assert not [path for path in PACKAGE_ROOT.rglob("*.tar.gz")]
