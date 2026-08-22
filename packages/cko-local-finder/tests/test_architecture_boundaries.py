from __future__ import annotations

import ast
from pathlib import Path
import tomllib


PROJECT = Path(__file__).parents[1]
ROOT = PROJECT.parents[1]
SOURCE = PROJECT / "src" / "cko_local_finder"


def _absolute_import_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_four_architecture_namespaces_exist() -> None:
    for name in ("domain", "application", "infrastructure", "cli"):
        assert (SOURCE / name / "__init__.py").is_file()


def test_dependency_direction_and_forbidden_imports() -> None:
    forbidden = {"cko", "cko_fcp"}
    for path in SOURCE.rglob("*.py"):
        roots = _absolute_import_roots(path)
        assert not roots & forbidden, f"forbidden import in {path}: {roots & forbidden}"
        relative = path.relative_to(SOURCE).parts
        if relative[0] == "domain":
            assert not roots & {"application", "infrastructure", "cli"}


def test_only_authorized_adapters_and_functional_cli() -> None:
    allowed = {"__init__.py", "filesystem.py", "hashing.py", "migrations.py", "sqlite.py", "extractors.py", "text.py", "search.py", "reporting.py"}
    assert {path.name for path in (SOURCE / "infrastructure").glob("*.py")} == allowed
    assert {path.name for path in (SOURCE / "cli").glob("*.py")} == {
        "__init__.py", "main.py", "runtime.py", "presenters.py",
    }
    metadata = tomllib.loads((PROJECT / "pyproject.toml").read_text(encoding="utf-8"))
    assert metadata["project"]["scripts"] == {"cko-local-finder": "cko_local_finder.cli.main:main"}
    assert metadata["project"]["dependencies"] == ["pypdf>=5,<7", "python-docx>=1.1,<2"]


def test_distribution_isolated_from_core() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "cko-local-finder" not in metadata["project"].get("dependencies", [])
    assert not (PROJECT / "src" / "cko").exists()
