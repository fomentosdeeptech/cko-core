from __future__ import annotations

import ast
import os
from pathlib import Path
import subprocess
import sys
import tomllib


PACKAGE_ROOT = Path(__file__).parents[1]
PRODUCTION_ROOT = PACKAGE_ROOT / "src" / "cko_local_finder"


def _production_sources() -> list[Path]:
    return sorted(PRODUCTION_ROOT.rglob("*.py"))


def test_production_remains_contract_skeleton() -> None:
    expected = {
        "__init__.py", "application/__init__.py", "application/ports.py",
        "cli/__init__.py", "domain/__init__.py", "domain/models.py",
        "application/discovery.py", "application/duplicates.py",
        "infrastructure/__init__.py", "infrastructure/filesystem.py",
        "infrastructure/hashing.py",
    }
    actual = {path.relative_to(PRODUCTION_ROOT).as_posix() for path in _production_sources()}
    assert actual == expected


def test_no_forbidden_production_capabilities_or_imports() -> None:
    forbidden_imports = {"pypdf", "docx", "sqlite3", "click", "typer", "sqlalchemy"}
    forbidden_calls = {"connect", "execute", "extract", "index", "search"}
    for path in _production_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not ({alias.name.split(".")[0] for alias in node.names} & forbidden_imports)
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden_imports
            elif isinstance(node, ast.Call):
                name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                assert name not in forbidden_calls


def test_no_runtime_dependency_added() -> None:
    project = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["dependencies"] == []
    assert project["optional-dependencies"] == {"test": ["pytest>=8,<9"]}


def test_importing_factory_creates_no_files(tmp_path: Path) -> None:
    tests_parent = str(PACKAGE_ROOT)
    env = os.environ.copy()
    env["PYTHONPATH"] = tests_parent
    code = "import tests.corpus_factory"
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=tmp_path, env=env,
        check=False, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert list(tmp_path.iterdir()) == []


def test_p01903_scope_and_root_api_remain_narrow() -> None:
    import cko_local_finder

    assert cko_local_finder.__all__ == ("__version__",)
    production = "\n".join(path.read_text(encoding="utf-8").lower() for path in _production_sources())
    for forbidden in ("pypdf", "python-docx", "sqlite", "fts5", "create table", "argparse"):
        assert forbidden not in production
    assert not any((PRODUCTION_ROOT / "infrastructure").glob("*extract*"))
    assert not any((PRODUCTION_ROOT / "infrastructure").glob("*persist*"))
