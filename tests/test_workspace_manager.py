"""Tests for the SPR-008OA canonical development workspace infrastructure."""

from __future__ import annotations

import ast
import inspect
import logging
import zipfile
from pathlib import Path

import pytest

from cko.core.workspace import (
    EnvironmentValidator,
    RuntimePaths,
    TemporaryFileManager,
    WorkspaceCleaner,
    WorkspaceManager,
)
from cko.core.workspace.cli import main
from cko.core.workspace.build import build_wheel


def create_file(path: Path, content: str = "temporário") -> Path:
    """Create one UTF-8 fixture and return its path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_paths_are_centralized_canonical_and_immutable(tmp_path: Path) -> None:
    paths = RuntimePaths.from_root(tmp_path)
    assert paths.canonical_directories == (
        tmp_path / "runtime",
        tmp_path / "runtime" / "temp",
        tmp_path / "runtime" / "cache",
        tmp_path / "runtime" / "traces",
        tmp_path / "runtime" / "logs",
        tmp_path / "runtime" / "reports",
        tmp_path / "runtime" / "database",
        tmp_path / "runtime" / "snapshots",
    )
    assert paths.database in paths.permanent_directories
    with pytest.raises(AttributeError):
        paths.temp = tmp_path


def test_workspace_create_locate_and_idempotency(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path)
    created = manager.create()
    assert created == manager.paths.canonical_directories
    assert manager.create() == ()
    assert all(item.is_dir() for item in manager.paths.canonical_directories)
    assert manager.locate("traces") == tmp_path / "runtime" / "traces"
    with pytest.raises(KeyError, match="unknown"):
        manager.locate("invalid")


def test_workspace_discovery_supports_manifest_and_environment(tmp_path: Path) -> None:
    project = tmp_path / "manifest-project"
    child = project / "src" / "package"
    child.mkdir(parents=True)
    (project / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    assert RuntimePaths.discover(child).root == project.resolve()
    assert RuntimePaths.discover(project / "pyproject.toml").root == project.resolve()
    override = tmp_path / "override"
    assert RuntimePaths.discover(child, environ={
        "CKO_WORKSPACE_ROOT": str(override),
    }).root == override.resolve()


def test_workspace_rejects_collision_and_conflicting_configuration(
    tmp_path: Path,
) -> None:
    manager = WorkspaceManager(tmp_path)
    create_file(manager.paths.runtime)
    with pytest.raises(NotADirectoryError):
        manager.create()
    with pytest.raises(ValueError, match="not both"):
        WorkspaceManager(tmp_path, paths=RuntimePaths.from_root(tmp_path))


def test_permission_validation_writes_reads_and_removes_utf8(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path)
    assert manager.validate_permissions()
    assert not tuple(manager.paths.temp.iterdir())


def test_complete_cleanup_removes_only_temporary_artifacts(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path)
    manager.create()
    temporary = (
        create_file(manager.paths.temp / "session.tmp"),
        create_file(manager.paths.cache / "cache.bin"),
        create_file(manager.paths.traces / "run.json"),
        create_file(tmp_path / "src" / "__pycache__" / "module.pyc"),
        create_file(tmp_path / ".pytest_cache" / "state"),
        create_file(tmp_path / ".cover"),
        create_file(tmp_path / "legacy_test_temp" / "fixture.tmp"),
        create_file(tmp_path / "trace" / "trace.json"),
    )
    permanent = tuple(
        create_file(directory / "keep.txt")
        for directory in manager.paths.permanent_directories
    )
    result = manager.clean()
    assert result.count >= 8
    assert all(not item.exists() for item in temporary)
    assert all(item.exists() for item in permanent)
    assert all(item.is_dir() for item in manager.paths.canonical_directories)


def test_individual_cleanup_operations_are_isolated(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path)
    manager.create()
    temp = create_file(manager.paths.temp / "temp.txt")
    cache = create_file(manager.paths.cache / "cache.txt")
    trace = create_file(manager.paths.traces / "trace.txt")
    python_cache = create_file(tmp_path / "pkg" / "module.pyo")
    cleaner = WorkspaceCleaner(manager)
    assert cleaner.clean_temp().removed == (temp,)
    assert cache.exists() and trace.exists() and python_cache.exists()
    assert cleaner.clean_cache().removed == (cache,)
    assert cleaner.clean_trace().removed == (trace,)
    assert cleaner.clean_python_cache().removed == (python_cache,)


def test_dry_run_reports_without_modifying_anything(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path)
    manager.create()
    artifact = create_file(manager.paths.temp / "preview.tmp")
    result = WorkspaceCleaner(manager).dry_run()
    assert result.dry_run and result.count == 1
    assert result.removed == ()
    assert result.candidates == (artifact,)
    assert artifact.exists()


def test_safety_rejects_root_outside_and_permanent_paths(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path / "project")
    manager.create()
    temporary = TemporaryFileManager(manager)
    assert not temporary.is_safe(manager.paths.root)
    assert not temporary.is_safe(tmp_path / "outside.tmp")
    assert not temporary.is_safe(manager.paths.database / "cko.db")
    assert temporary.is_safe(manager.paths.temp / "session.tmp")


def test_required_logging_events_are_emitted(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    manager = WorkspaceManager(tmp_path)
    with caplog.at_level(logging.INFO):
        manager.create()
        create_file(manager.paths.cache / "cache.tmp")
        create_file(manager.paths.traces / "trace.tmp")
        manager.cleaner().clean_cache()
        manager.cleaner().clean_trace()
        EnvironmentValidator(
            manager,
            minimum_free_bytes=0,
            powershell_version=lambda: (5, 1),
        ).validate()
        manager.clean()
    events = {getattr(item, "event", None) for item in caplog.records}
    assert {
        "workspace_created", "workspace_cleaned", "cache_removed",
        "trace_removed", "validation_completed",
    } <= events


def test_environment_validation_covers_all_requirements(tmp_path: Path) -> None:
    manager = WorkspaceManager(tmp_path)
    result = EnvironmentValidator(
        manager,
        minimum_free_bytes=0,
        powershell_version=lambda: (5, 1),
    ).validate()
    assert result.valid
    assert {item.name for item in result.checks} == {
        "python", "powershell", "permissions", "encoding", "disk_space",
    }
    assert all(item.value and item.requirement for item in result.checks)


def test_environment_validation_reports_failure_without_raising(
    tmp_path: Path,
) -> None:
    manager = WorkspaceManager(tmp_path)
    result = EnvironmentValidator(
        manager,
        minimum_free_bytes=10**30,
        powershell_version=lambda: (),
    ).validate()
    assert not result.valid
    failed = {item.name for item in result.checks if not item.passed}
    assert {"powershell", "disk_space"} <= failed
    with pytest.raises(ValueError, match="non-negative"):
        EnvironmentValidator(manager, minimum_free_bytes=-1)


def test_cli_initializes_validates_and_previews_cleanup(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(("--root", str(tmp_path), "init")) == 0
    create_file(tmp_path / "runtime" / "temp" / "cli.tmp")
    assert main(("--root", str(tmp_path), "clean", "--dry-run")) == 0
    output = capsys.readouterr().out
    assert '"dry_run": true' in output
    assert "cli.tmp" in output


def test_cli_validation_uses_installed_python_and_powershell(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(("--root", str(tmp_path), "validate")) == 0
    output = capsys.readouterr().out
    assert '"valid": true' in output
    assert '"name": "python"' in output
    assert '"name": "powershell"' in output


def test_cmd_scripts_are_executable_and_isolate_runtime() -> None:
    root = Path(__file__).parents[1]
    expected = {"CKO_CLEAN.cmd", "CKO_TESTS.cmd", "CKO_BUILD.cmd", "CKO_RUNTIME.cmd"}
    for name in expected:
        content = (root / name).read_text(encoding="utf-8")
        assert "@echo off" in content
        assert 'set "PYTHONUTF8=1"' in content
        assert 'set "PYTHONPATH=%~dp0src"' in content
        assert "exit /b %CKO_EXIT_CODE%" in content


def test_dependency_free_build_creates_a_valid_deterministic_wheel(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    create_file(
        project / "pyproject.toml",
        """[project]
name = "sample-cko"
version = "1.2.3"
description = "Pacote canônico"
requires-python = ">=3.13"
""",
    )
    create_file(project / "src" / "sample_cko" / "__init__.py", "VALUE = 'á'\n")
    manager = WorkspaceManager(project)
    first = build_wheel(manager)
    first_bytes = first.artifact.read_bytes()
    second = build_wheel(manager)
    assert first.artifact == second.artifact
    assert first_bytes == second.artifact.read_bytes()
    with zipfile.ZipFile(second.artifact) as archive:
        names = archive.namelist()
        assert "sample_cko/__init__.py" in names
        assert "sample_cko-1.2.3.dist-info/METADATA" in names
        assert "sample_cko-1.2.3.dist-info/RECORD" in names
        assert "Pacote canônico" in archive.read(names[-3]).decode("utf-8")


def test_cli_build_command_uses_canonical_reports_folder(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    create_file(
        tmp_path / "pyproject.toml",
        '[project]\nname = "cli-build"\nversion = "1.0.0"\n',
    )
    create_file(tmp_path / "src" / "cli_build" / "__init__.py", "")
    assert main(("--root", str(tmp_path), "build")) == 0
    output = capsys.readouterr().out
    assert "cli_build-1.0.0-py3-none-any.whl" in output
    assert (tmp_path / "runtime" / "reports" / "build").is_dir()


def test_public_internal_surface_utf8_pep8_docstrings_and_type_hints() -> None:
    public = (
        RuntimePaths, WorkspaceManager, TemporaryFileManager,
        WorkspaceCleaner, EnvironmentValidator,
    )
    assert all(inspect.getdoc(item) for item in public)
    assert inspect.signature(WorkspaceCleaner.clean).return_annotation is not (
        inspect.Signature.empty
    )
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "workspace"
    for path in root.glob("*.py"):
        content = path.read_bytes()
        assert not content.startswith(b"\xef\xbb\xbf")
        text = content.decode("utf-8")
        assert max(map(len, text.splitlines())) <= 99
        ast.parse(text)
        assert "TODO" not in text
