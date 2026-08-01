"""Certification tests for the SPR-009A CKO CORE v1.0 consolidation."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import tomllib
import zipfile
from pathlib import Path
from types import MappingProxyType

import pytest

import cko.core as core
from cko.core.checkpoint import DefaultCheckpointEngine
from cko.core.composition import (
    BuildInfrastructure,
    CompositionRoot,
    CoreComposition,
    CoreCompositionSettings,
    compose_core,
)
from cko.core.connectors import ConnectorException
from cko.core.discovery import (
    ExecutionPlannerError,
    LogicalIndexError,
    OptimizerError,
    PlannerError,
    StatisticsError,
)
from cko.core.exceptions import CKOError, CompositionError
from cko.core.execution import ExecutionEngine, ExecutionEngineError
from cko.core.runtime import Runtime, RuntimeErrorBase
from cko.core.storage import StorageException
from cko.core.storage.filesystem import FILESYSTEM_IDENTIFIER
from cko.core.storage.sqlite import SQLITE_IDENTIFIER
from cko.core.uow import DefaultUnitOfWork, UnitOfWorkException
from cko.core.workspace import WorkspaceManager


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _core_exception_classes() -> tuple:
    classes: set[type[BaseException]] = set()
    for module_info in pkgutil.walk_packages(
        core.__path__,
        prefix=f"{core.__name__}.",
    ):
        module = importlib.import_module(module_info.name)
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if (
                candidate.__module__ == module.__name__
                and issubclass(candidate, BaseException)
            ):
                classes.add(candidate)
    return tuple(sorted(classes, key=lambda item: item.__qualname__))


def test_official_version_is_consistent() -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]
    metadata = (
        PROJECT_ROOT / "src" / "cko.egg-info" / "PKG-INFO"
    ).read_text(encoding="utf-8")

    assert project["version"] == "1.0.0"
    assert core.__version__ == "1.0.0"
    assert "Version: 1.0.0\n" in metadata
    assert "Requires-Python: >=3.13\n" in metadata


def test_every_declared_core_exception_has_one_canonical_root() -> None:
    declared = _core_exception_classes()

    assert declared
    assert all(issubclass(item, CKOError) for item in declared)
    assert CompositionError in declared


@pytest.mark.parametrize(
    "error_type",
    (
        ExecutionPlannerError,
        LogicalIndexError,
        OptimizerError,
        PlannerError,
        StatisticsError,
        ExecutionEngineError,
    ),
)
def test_value_error_compatibility_is_preserved(
    error_type: type[BaseException],
) -> None:
    assert issubclass(error_type, CKOError)
    assert issubclass(error_type, ValueError)


@pytest.mark.parametrize(
    "error_type",
    (
        ConnectorException,
        RuntimeErrorBase,
        StorageException,
        UnitOfWorkException,
    ),
)
def test_domain_roots_converge_on_cko_error(
    error_type: type[BaseException],
) -> None:
    assert issubclass(error_type, CKOError)


def test_composition_root_builds_the_complete_graph(tmp_path: Path) -> None:
    settings = CoreCompositionSettings(
        workspace_root=tmp_path,
        configure_logging=False,
    )
    composition = compose_core(settings)

    assert isinstance(composition, CoreComposition)
    assert isinstance(composition.build, BuildInfrastructure)
    assert isinstance(composition.runtime, Runtime)
    assert isinstance(composition.execution_engine, ExecutionEngine)
    assert isinstance(composition.checkpoint, DefaultCheckpointEngine)
    assert isinstance(composition.unit_of_work, DefaultUnitOfWork)
    assert set(composition.storages) == {
        FILESYSTEM_IDENTIFIER,
        SQLITE_IDENTIFIER,
    }
    assert set(composition.connectors) == {
        FILESYSTEM_IDENTIFIER,
        SQLITE_IDENTIFIER,
    }
    assert len(composition.discovery_registry) == 0
    assert len(composition.validators) == 16
    assert isinstance(composition.validators, MappingProxyType)
    assert composition.checkpoint_repository is not None
    assert composition.environment_validator.manager is composition.workspace


def test_composition_root_is_the_factory_for_fresh_lifecycles(
    tmp_path: Path,
) -> None:
    composition = CompositionRoot.compose(
        CoreCompositionSettings(
            workspace_root=tmp_path,
            configure_logging=False,
        )
    )

    assert composition.create_runtime() is not composition.runtime
    assert composition.create_unit_of_work() is not composition.unit_of_work
    assert len(composition.create_unit_of_work().repositories) == 5


def test_invalid_checkpoint_storage_fails_at_the_root(
    tmp_path: Path,
) -> None:
    settings = CoreCompositionSettings(
        workspace_root=tmp_path,
        checkpoint_storage_id="unregistered",
        configure_logging=False,
    )

    with pytest.raises(CompositionError):
        compose_core(settings)


def test_official_builder_emits_v1_wheel_and_metadata(
    tmp_path: Path,
) -> None:
    result = BuildInfrastructure(
        WorkspaceManager(PROJECT_ROOT)
    ).build(tmp_path)

    assert result.artifact.name == "cko-1.0.0-py3-none-any.whl"
    with zipfile.ZipFile(result.artifact) as archive:
        metadata = archive.read(
            "cko-1.0.0.dist-info/METADATA"
        ).decode("utf-8")
        names = set(archive.namelist())
    assert "Version: 1.0.0\n" in metadata
    assert "Requires-Python: >=3.13\n" in metadata
    assert "cko/core/composition/__init__.py" in names
    assert "cko/core/composition/models.py" in names
    assert "cko/core/composition/root.py" in names


def test_public_facade_exposes_the_certified_composition_api() -> None:
    expected = {
        "BuildInfrastructure",
        "CKOError",
        "CompositionError",
        "CompositionRoot",
        "CoreComposition",
        "CoreCompositionSettings",
        "compose_core",
    }

    assert expected <= set(core.__all__)
    assert all(hasattr(core, name) for name in expected)
