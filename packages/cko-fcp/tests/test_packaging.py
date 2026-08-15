from __future__ import annotations

import ast
import importlib.metadata
from pathlib import Path
import tomllib
import unittest

import cko_fcp


PROJECT = Path(__file__).parents[1]
SOURCE = PROJECT / "src" / "cko_fcp"
ROOT = PROJECT.parents[1]


class PackagingContractTest(unittest.TestCase):
    def test_package_import_and_distribution_identity(self) -> None:
        self.assertEqual(cko_fcp.DISTRIBUTION_VERSION, "0.1.0")
        self.assertEqual(importlib.metadata.version("cko-fcp"), "0.1.0")

    def test_distribution_has_no_runtime_dependencies(self) -> None:
        self.assertEqual(importlib.metadata.requires("cko-fcp"), None)

    def test_packaging_is_distribution_local(self) -> None:
        metadata = tomllib.loads((PROJECT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(metadata["project"]["name"], "cko-fcp")
        self.assertEqual(metadata["tool"]["setuptools"]["package-dir"], {"": "src"})
        self.assertEqual(metadata["tool"]["setuptools"]["packages"]["find"]["where"], ["src"])

    def test_root_distribution_does_not_depend_on_cko_fcp(self) -> None:
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertNotIn("cko-fcp", metadata["project"].get("dependencies", []))

    def test_no_namespace_aliases_or_shadowing(self) -> None:
        self.assertFalse((PROJECT / "src" / "cko").exists())
        self.assertFalse((PROJECT / "src" / "fcp").exists())
        self.assertFalse((ROOT / "external" / "fcp").exists())

    def test_standard_library_only_and_no_io_capabilities(self) -> None:
        forbidden = {
            "cko", "pathlib", "socket", "urllib", "http", "requests", "subprocess",
            "sqlite3", "os", "io", "httpx", "sqlalchemy",
        }
        for path in SOURCE.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            roots: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    roots.add(node.module.split(".")[0])
            self.assertFalse(roots & forbidden, f"forbidden dependency in {path}: {roots & forbidden}")

    def test_no_credentials_or_p_018_02_modules(self) -> None:
        forbidden_names = {
            "authority", "authorization", "credentials", "database", "network",
            "publication_service", "query_service",
        }
        module_names = {path.stem for path in SOURCE.glob("*.py")}
        self.assertFalse(module_names & forbidden_names)

    def test_public_surface_is_owned_by_cko_fcp(self) -> None:
        self.assertIn("DISTRIBUTION_VERSION", cko_fcp.__all__)
        self.assertNotIn("cko_fcp", cko_fcp.__all__)


if __name__ == "__main__":
    unittest.main()
