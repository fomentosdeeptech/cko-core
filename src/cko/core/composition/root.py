"""Single official composition root for the CKO CORE SDK."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Mapping

from cko.core.checkpoint import (
    CheckpointValidator,
    DefaultCheckpointEngine,
    DefaultCheckpointSerializer,
    StorageCheckpointRepository,
)
from cko.core.connectors import (
    Connector,
    ConnectorFactory,
    ConnectorRegistry,
    ConnectorValidator,
)
from cko.core.discovery import (
    CostBasedPlanner,
    DefaultDiscoveryValidator,
    DiscoveryProviderFactory,
    DiscoveryProviderRegistry,
    DiscoveryProviderResolver,
    DiscoveryService,
    ExecutionPipeline as PhysicalExecutionPlanner,
    ExecutionPlanValidator,
    LogicalIndexValidator,
    OptimizationPipeline,
    OptimizerValidator,
    PlannerValidator,
    StatisticsValidator,
)
from cko.core.execution import ExecutionEngine, ExecutionEngineValidator
from cko.core.exceptions import CompositionError
from cko.core.inventory import InventoryValidator
from cko.core.logging import configure_logging, get_logger
from cko.core.models import CanonicalEvent
from cko.core.runtime import Runtime, RuntimeValidator
from cko.core.storage import (
    Storage,
    StorageFactory,
    StorageRegistry,
    StorageValidator,
)
from cko.core.storage.filesystem import (
    FilesystemStorageFactory,
    FilesystemStorageValidator,
)
from cko.core.storage.sqlite import (
    SQLiteStorageFactory,
    SQLiteStorageValidator,
)
from cko.core.uow import (
    DefaultUnitOfWork,
    UnitOfWorkContext,
    UnitOfWorkRepository,
    UnitOfWorkValidator,
)
from cko.core.workspace import EnvironmentValidator, WorkspaceManager
from cko.core.workspace.build import BuildResult, build_wheel

from .models import CoreCompositionSettings


class _LoggingDiscoveryEventPublisher:
    """Publish Discovery events through the composed structured logger."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def publish(self, event: CanonicalEvent) -> None:
        self._logger.info(
            event.name,
            extra={
                "event": event.name,
                "context": {"event_id": str(event.id)},
            },
        )


@dataclass(frozen=True, slots=True)
class BuildInfrastructure:
    """Bind deterministic wheel construction to the composed workspace."""

    workspace: WorkspaceManager

    def build(self, output: str | Path | None = None) -> BuildResult:
        """Build the official wheel in the bound workspace."""
        return build_wheel(self.workspace, output)


@dataclass(frozen=True, slots=True)
class CoreComposition:
    """Expose the complete, immutable graph assembled by the root."""

    settings: CoreCompositionSettings
    logger: logging.Logger
    workspace: WorkspaceManager
    build: BuildInfrastructure
    environment_validator: EnvironmentValidator
    validators: Mapping[str, object]
    connector_registry: ConnectorRegistry
    connector_factory: ConnectorFactory
    connectors: Mapping[str, Connector]
    storage_registry: StorageRegistry
    storage_factory: StorageFactory
    storages: Mapping[str, Storage]
    discovery_registry: DiscoveryProviderRegistry
    discovery_factory: DiscoveryProviderFactory
    discovery: DiscoveryService
    planner: CostBasedPlanner
    optimizer: OptimizationPipeline
    execution_planner: PhysicalExecutionPlanner
    execution_engine: ExecutionEngine
    checkpoint_repository: StorageCheckpointRepository
    checkpoint: DefaultCheckpointEngine
    unit_of_work_repositories: tuple
    unit_of_work: DefaultUnitOfWork
    runtime: Runtime

    def create_runtime(
        self,
        *,
        runtime_id: str | None = None,
        session_id: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> Runtime:
        """Create a fresh Runtime through the official composition policy."""
        return Runtime(
            self.execution_engine,
            runtime_id=runtime_id,
            session_id=session_id,
            metadata=metadata,
            validator=RuntimeValidator(),
        )

    def create_unit_of_work(
        self,
        context: UnitOfWorkContext | None = None,
    ) -> DefaultUnitOfWork:
        """Create a fresh Unit of Work with all composed public ports."""
        return DefaultUnitOfWork(
            self.unit_of_work_repositories,
            context=context,
            validator=UnitOfWorkValidator(),
        )


class CompositionRoot:
    """Assemble every official CKO CORE component in one deterministic graph."""

    @classmethod
    def compose(
        cls,
        settings: CoreCompositionSettings | None = None,
    ) -> CoreComposition:
        """Create and validate the complete CKO CORE object graph."""
        selected = settings or CoreCompositionSettings()
        if not isinstance(selected, CoreCompositionSettings):
            raise CompositionError(
                "settings must be CoreCompositionSettings"
            )
        workspace = WorkspaceManager(selected.workspace_root)
        workspace.create()
        if selected.configure_logging:
            logger = configure_logging(selected.log_level)
        else:
            logger = logging.getLogger("cko")

        validators = cls._validators(workspace)
        connector_registry = ConnectorRegistry(validators["connector"])
        storage_registry = StorageRegistry(validators["storage"])

        filesystem_root = (
            workspace.paths.snapshots
            if selected.filesystem_root is None
            else Path(selected.filesystem_root).expanduser().resolve()
        )
        sqlite_database = (
            workspace.paths.database / "cko-core.db"
            if selected.sqlite_database is None
            else Path(selected.sqlite_database).expanduser().resolve()
        )
        filesystem = FilesystemStorageFactory(
            filesystem_root,
            validator=validators["filesystem"],
        )
        sqlite = SQLiteStorageFactory(
            sqlite_database,
            validator=validators["sqlite"],
            timeout=selected.sqlite_timeout,
        )
        adapter_factories = (filesystem, sqlite)
        for adapter in adapter_factories:
            connector_registry.register(
                adapter.descriptor.connector,
                adapter.create_connector,
            )
            storage_registry.register(
                adapter.descriptor.storage,
                adapter.create_storage,
            )

        connector_factory = ConnectorFactory(
            connector_registry,
            validators["connector"],
        )
        storage_factory = StorageFactory(
            storage_registry,
            validators["storage"],
        )
        connectors = MappingProxyType({
            descriptor.identifier: connector_factory.create(
                descriptor.identifier
            )
            for descriptor in connector_registry.descriptors()
        })
        storages = MappingProxyType({
            descriptor.identifier: storage_factory.create(
                descriptor.identifier
            )
            for descriptor in storage_registry.descriptors()
        })
        try:
            checkpoint_storage = storages[selected.checkpoint_storage_id]
        except KeyError as error:
            raise CompositionError(
                "checkpoint_storage_id is not registered"
            ) from error

        serializer = DefaultCheckpointSerializer()
        checkpoint_repository = StorageCheckpointRepository(
            checkpoint_storage,
            serializer=serializer,
            validator=validators["checkpoint"],
        )
        checkpoint = DefaultCheckpointEngine(
            checkpoint_repository,
            serializer=serializer,
            validator=validators["checkpoint"],
        )
        repositories = tuple(
            UnitOfWorkRepository(
                identifier=f"storage:{identifier}",
                repository=storage,
            )
            for identifier, storage in storages.items()
        ) + tuple(
            UnitOfWorkRepository(
                identifier=f"connector:{identifier}",
                repository=connector,
            )
            for identifier, connector in connectors.items()
        ) + (
            UnitOfWorkRepository(
                identifier="checkpoint",
                repository=checkpoint_repository,
            ),
        )
        unit_of_work = DefaultUnitOfWork(
            repositories,
            validator=validators["unit_of_work"],
        )

        discovery_registry = DiscoveryProviderRegistry()
        discovery_factory = DiscoveryProviderFactory(
            discovery_registry,
            DiscoveryProviderResolver(),
        )
        discovery = DiscoveryService(
            validators["discovery"],
            _LoggingDiscoveryEventPublisher(
                get_logger("core.discovery.events")
            ),
            lambda: datetime.now(UTC),
        )
        planner = CostBasedPlanner()
        optimizer = OptimizationPipeline(
            validator=validators["optimizer"]
        )
        execution_planner = PhysicalExecutionPlanner()
        execution_engine = ExecutionEngine(
            validator=validators["execution_engine"]
        )
        runtime = Runtime(
            execution_engine,
            validator=validators["runtime"],
        )
        logger.info(
            "composition_completed",
            extra={
                "event": "core.composition.completed",
                "context": {
                    "connectors": len(connectors),
                    "storages": len(storages),
                    "version": "1.0.0",
                },
            },
        )
        return CoreComposition(
            settings=selected,
            logger=logger,
            workspace=workspace,
            build=BuildInfrastructure(workspace),
            environment_validator=validators["environment"],
            validators=MappingProxyType(dict(validators)),
            connector_registry=connector_registry,
            connector_factory=connector_factory,
            connectors=connectors,
            storage_registry=storage_registry,
            storage_factory=storage_factory,
            storages=storages,
            discovery_registry=discovery_registry,
            discovery_factory=discovery_factory,
            discovery=discovery,
            planner=planner,
            optimizer=optimizer,
            execution_planner=execution_planner,
            execution_engine=execution_engine,
            checkpoint_repository=checkpoint_repository,
            checkpoint=checkpoint,
            unit_of_work_repositories=repositories,
            unit_of_work=unit_of_work,
            runtime=runtime,
        )

    @staticmethod
    def _validators(
        workspace: WorkspaceManager,
    ) -> dict[str, object]:
        return {
            "checkpoint": CheckpointValidator(),
            "connector": ConnectorValidator(),
            "discovery": DefaultDiscoveryValidator(),
            "environment": EnvironmentValidator(workspace),
            "execution_engine": ExecutionEngineValidator(),
            "execution_plan": ExecutionPlanValidator(),
            "filesystem": FilesystemStorageValidator(),
            "inventory": InventoryValidator(),
            "logical_index": LogicalIndexValidator(),
            "optimizer": OptimizerValidator(),
            "planner": PlannerValidator(),
            "runtime": RuntimeValidator(),
            "sqlite": SQLiteStorageValidator(),
            "statistics": StatisticsValidator(),
            "storage": StorageValidator(),
            "unit_of_work": UnitOfWorkValidator(),
        }


compose_core: Callable[
    [CoreCompositionSettings | None], CoreComposition
] = CompositionRoot.compose


__all__ = [
    "BuildInfrastructure",
    "CompositionRoot",
    "CoreComposition",
    "compose_core",
]
