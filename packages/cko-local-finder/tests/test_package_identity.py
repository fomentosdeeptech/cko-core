from __future__ import annotations

import ast
import importlib.resources
from pathlib import Path
import sys
import tomllib

import cko_local_finder


PROJECT = Path(__file__).parents[1]
SOURCE = PROJECT / "src" / "cko_local_finder"


def test_package_identity_and_public_api() -> None:
    assert cko_local_finder.__version__ == "0.1.0"
    assert cko_local_finder.__all__ == ("__version__",)
    assert set(cko_local_finder.__all__) == {"__version__"}


def test_single_installed_entry_point_metadata() -> None:
    metadata = tomllib.loads((PROJECT / "pyproject.toml").read_text(encoding="utf-8"))
    assert metadata["project"]["scripts"] == {
        "cko-local-finder": "cko_local_finder.cli.main:main"
    }


def test_typed_package_marker_is_packaged() -> None:
    marker = importlib.resources.files("cko_local_finder").joinpath("py.typed")
    assert marker.is_file()


def test_import_has_no_package_side_effects_or_external_dependencies() -> None:
    tree = ast.parse((SOURCE / "__init__.py").read_text(encoding="utf-8"))
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    assert imports == []
    assert calls == []
    assert "cko" not in sys.modules
