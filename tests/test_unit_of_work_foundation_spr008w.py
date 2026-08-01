"""Dedicated validation suite for SPR-008W Unit of Work foundation."""

from __future__ import annotations

import ast
import logging
from datetime import datetime, timezone
from pathlib import Path

import pytest

from cko.core.checkpoint import CheckpointRepository
from cko.core.connectors import (
    Connector,
    ConnectorCapabilities,
    ConnectorDescriptor,
    ConnectorMetadata,
)
from cko.core.storage import (
    Storage,
    StorageCapabilities,
    StorageDescriptor,
    StorageMetadata,
    StorageOperation,
)
from cko.core.uow import (
    UOW_SCHEMA_VERSION,
    UOW_VERSION,
    DefaultUnitOfWork,
    UnitOfWork,
    UnitOfWorkClosedError,
    UnitOfWorkContext,
    UnitOfWorkException,
    UnitOfWorkExecutionError,
    UnitOfWorkOperation,
    UnitOfWorkRegistrationError,
    UnitOfWorkRepository,
    UnitOfWorkResult,
    UnitOfWorkRollbackError,
    UnitOfWorkState,
    UnitOfWorkStateError,
    UnitOfWorkValidationError,
    UnitOfWorkValidator,
)


INSTANT = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)


class MemoryCheckpointRepository(CheckpointRepository):
    """Minimal CheckpointRepository test double."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def store(self, record):
        self.calls.append("store")
        return record

    def restore(self, identifier):
        self.calls.append("restore")
        return identifier

    def list(self, query):
        self.calls.append("list")
        return query

    def inspect(self, identifier):
        self.calls.append("inspect")
        return identifier

    def delete(self, identifier):
        self.calls.append("delete")
        return identifier


class MemoryStorage(Storage):
    """Minimal Storage test double."""

    def __init__(self, identifier: str = "memory.storage") -> None:
        self._descriptor = StorageDescriptor(
            identifier=identifier,
            metadata=StorageMetadata("Memory", "Test storage", "1.0"),
            capabilities=StorageCapabilities(tuple(StorageOperation)),
        )
        self.calls: list[object] = []

    @property
    def descriptor(self) -> StorageDescriptor:
        return self._descriptor

    def execute(self, session):
        self.calls.append(session)
        return session


class MemoryConnector(Connector):
    """Minimal Connector test double."""

    def __init__(self, identifier: str = "memory.connector") -> None:
        self._descriptor = ConnectorDescriptor(
            identifier=identifier,
            metadata=ConnectorMetadata("Memory", "Test connector", "1.0"),
            capabilities=ConnectorCapabilities(("read", "write")),
        )
        self.calls: list[object] = []

    @property
    def descriptor(self) -> ConnectorDescriptor:
        return self._descriptor

    def execute(self, session):
        self.calls.append(session)
        return session


def registration(identifier="checkpoints", resource=None):
    """Create one valid public port registration."""
    return UnitOfWorkRepository(
        identifier,
        MemoryCheckpointRepository() if resource is None else resource,
    )


def operation(
    operation_id="op-1",
    repository_id="checkpoints",
    action=None,
    compensation=None,
):
    """Create one valid logical operation."""
    callback = (
        (lambda repository, context: "value")
        if action is None
        else action
    )
    return UnitOfWorkOperation(
        operation_id,
        repository_id,
        callback,
        compensation,
    )


def uow(*repositories):
    """Create a deterministic Unit of Work."""
    return DefaultUnitOfWork(
        repositories,
        clock=lambda: INSTANT,
        id_factory=lambda: "uow-1",
    )


def test_public_contract_models_and_versions() -> None:
    assert UOW_SCHEMA_VERSION == "1.0"
    assert UOW_VERSION == "1.0.0"
    assert issubclass(DefaultUnitOfWork, UnitOfWork)
    assert [state.value for state in UnitOfWorkState] == [
        "created",
        "started",
        "committed",
        "rolled_back",
        "closed",
        "failed",
    ]
    context = UnitOfWorkContext("uow-1", "corr-1", {"tag": ["a"]})
    assert context.metadata["tag"] == ("a",)
    with pytest.raises(TypeError):
        context.metadata["tag"] = "b"
    repository = registration()
    assert repository.kind == "checkpoint_repository"
    assert registration("storage", MemoryStorage()).kind == "storage"
    assert registration("connector", MemoryConnector()).kind == "connector"
    item = operation()
    assert callable(item.action)
    result = UnitOfWorkResult(
        True,
        UnitOfWorkState.CREATED,
        "uow_created",
        "uow-1",
        INSTANT,
    )
    assert result.timestamp is INSTANT


def test_begin_commit_close_and_history() -> None:
    work = uow(registration())
    assert work.status() is UnitOfWorkState.CREATED
    assert work.context.unit_of_work_id == "uow-1"
    assert work.begin().state is UnitOfWorkState.STARTED
    assert work.commit().state is UnitOfWorkState.COMMITTED
    assert work.close().state is UnitOfWorkState.CLOSED
    assert work.repositories == ()
    assert [item.event for item in work.history()] == [
        "uow_created",
        "uow_started",
        "uow_commit",
        "uow_closed",
    ]


def test_execute_multiple_public_port_families_and_commit() -> None:
    checkpoint = MemoryCheckpointRepository()
    storage = MemoryStorage()
    connector = MemoryConnector()
    work = uow(
        registration("checkpoint", checkpoint),
        registration("storage", storage),
        registration("connector", connector),
    )
    work.begin()
    seen = []
    for identifier, expected in (
        ("checkpoint", checkpoint),
        ("storage", storage),
        ("connector", connector),
    ):
        result = work.execute(
            operation(
                f"op-{identifier}",
                identifier,
                lambda resource, context, expected=expected: (
                    seen.append((resource, context)),
                    resource,
                )[1],
            )
        )
        assert result.value is expected
    committed = work.commit()
    assert committed.metadata["operation_count"] == 3
    assert [item[0] for item in seen] == [
        checkpoint,
        storage,
        connector,
    ]
    assert all(item[1] is work.context for item in seen)


def test_rollback_compensates_in_reverse_order() -> None:
    events = []
    work = uow(registration())
    work.begin()
    for index in range(3):
        work.execute(
            operation(
                f"op-{index}",
                action=lambda repository, context, value=index: (
                    events.append(f"do-{value}"),
                    value,
                )[1],
                compensation=lambda repository, value, context: events.append(
                    f"undo-{value}"
                ),
            )
        )
    result = work.rollback()
    assert result.state is UnitOfWorkState.ROLLED_BACK
    assert result.metadata == {
        "compensated_count": 3,
        "operation_count": 3,
    }
    assert events == [
        "do-0",
        "do-1",
        "do-2",
        "undo-2",
        "undo-1",
        "undo-0",
    ]


def test_context_manager_rolls_back_uncommitted_work_and_closes() -> None:
    events = []
    work = uow(registration())
    with work as active:
        active.execute(
            operation(
                action=lambda repository, context: events.append("do"),
                compensation=lambda repository, value, context: events.append(
                    "undo"
                ),
            )
        )
        assert active.status() is UnitOfWorkState.STARTED
    assert events == ["do", "undo"]
    assert work.status() is UnitOfWorkState.CLOSED
    assert "uow_rollback" in [item.event for item in work.history()]


def test_context_manager_preserves_exception_and_rolls_back() -> None:
    events = []
    work = uow(registration())
    with pytest.raises(RuntimeError, match="body failed"):
        with work:
            work.execute(
                operation(
                    action=lambda repository, context: events.append("do"),
                    compensation=lambda repository, value, context: (
                        events.append("undo")
                    ),
                )
            )
            raise RuntimeError("body failed")
    assert events == ["do", "undo"]
    assert work.status() is UnitOfWorkState.CLOSED


def test_context_manager_respects_explicit_commit() -> None:
    events = []
    work = uow(registration())
    with work:
        work.execute(
            operation(
                action=lambda repository, context: events.append("do"),
                compensation=lambda repository, value, context: events.append(
                    "undo"
                ),
            )
        )
        work.commit()
    assert events == ["do"]
    assert work.status() is UnitOfWorkState.CLOSED


def test_execute_failure_automatically_rolls_back_and_chains() -> None:
    events = []
    work = uow(registration())
    work.begin()
    work.execute(
        operation(
            "good",
            action=lambda repository, context: events.append("do"),
            compensation=lambda repository, value, context: events.append(
                "undo"
            ),
        )
    )

    def fail(repository, context):
        raise RuntimeError("provider failed")

    with pytest.raises(UnitOfWorkExecutionError) as captured:
        work.execute(operation("bad", action=fail))
    assert isinstance(captured.value.__cause__, RuntimeError)
    assert events == ["do", "undo"]
    assert work.status() is UnitOfWorkState.ROLLED_BACK
    assert "uow_failed" in [item.event for item in work.history()]


def test_unsuccessful_public_result_triggers_rollback() -> None:
    class FailedResult:
        success = False

    work = uow(registration())
    work.begin()
    with pytest.raises(
        UnitOfWorkExecutionError,
        match="unsuccessful result",
    ):
        work.execute(
            operation(action=lambda repository, context: FailedResult())
        )
    assert work.status() is UnitOfWorkState.ROLLED_BACK


def test_rollback_failure_is_best_effort_and_sets_failed_state() -> None:
    events = []
    work = uow(registration())
    work.begin()

    def bad_compensation(repository, value, context):
        events.append("bad")
        raise RuntimeError("cannot undo")

    work.execute(
        operation(
            "first",
            compensation=lambda repository, value, context: events.append(
                "good"
            ),
        )
    )
    work.execute(operation("second", compensation=bad_compensation))
    with pytest.raises(UnitOfWorkRollbackError) as captured:
        work.rollback()
    assert isinstance(captured.value.__cause__, RuntimeError)
    assert events == ["bad", "good"]
    assert work.status() is UnitOfWorkState.FAILED
    closed = work.close()
    assert work.status() is UnitOfWorkState.CLOSED
    assert closed.success


def test_nested_operations_are_protected_and_trigger_rollback() -> None:
    work = uow(registration())
    work.begin()

    def nested(repository, context):
        return work.execute(operation("inner"))

    with pytest.raises(UnitOfWorkExecutionError) as captured:
        work.execute(operation("outer", action=nested))
    assert isinstance(captured.value.__cause__, UnitOfWorkStateError)
    assert work.status() is UnitOfWorkState.ROLLED_BACK


def test_duplicate_begin_commit_rollback_and_close_are_rejected() -> None:
    work = uow(registration())
    work.begin()
    with pytest.raises(UnitOfWorkStateError):
        work.begin()
    work.commit()
    with pytest.raises(UnitOfWorkStateError):
        work.commit()
    with pytest.raises(UnitOfWorkStateError):
        work.rollback()
    work.close()
    with pytest.raises(UnitOfWorkClosedError):
        work.close()

    rolled_back = uow(registration())
    rolled_back.begin()
    rolled_back.rollback()
    with pytest.raises(UnitOfWorkStateError):
        rolled_back.rollback()


def test_register_unregister_clear_and_duplicate_validation() -> None:
    checkpoint = registration()
    work = uow()
    assert work.register(checkpoint) is checkpoint
    with pytest.raises(UnitOfWorkRegistrationError):
        work.register(checkpoint)
    with pytest.raises(UnitOfWorkRegistrationError):
        work.register(
            UnitOfWorkRepository("other", checkpoint.repository)
        )
    assert work.unregister("checkpoints") is checkpoint
    with pytest.raises(UnitOfWorkRegistrationError):
        work.unregister("missing")
    work.register(registration("one"))
    work.register(registration("two"))
    assert work.clear() == 2
    assert work.clear() == 0


def test_registration_and_operations_are_state_guarded() -> None:
    work = uow(registration())
    with pytest.raises(UnitOfWorkStateError):
        work.execute(operation())
    work.begin()
    with pytest.raises(UnitOfWorkRegistrationError):
        work.execute(operation(repository_id="missing"))
    work.execute(operation())
    with pytest.raises(UnitOfWorkExecutionError):
        work.execute(operation())
    with pytest.raises(UnitOfWorkRegistrationError):
        work.unregister("checkpoints")
    with pytest.raises(UnitOfWorkRegistrationError):
        work.clear()
    work.commit()
    with pytest.raises(UnitOfWorkStateError):
        work.register(registration("other"))
    work.close()
    with pytest.raises(UnitOfWorkClosedError):
        work.unregister("checkpoints")


def test_begin_context_identity_and_close_from_created() -> None:
    work = uow()
    replacement = UnitOfWorkContext("uow-1", "correlation")
    work.begin(replacement)
    assert work.context is replacement
    other = uow()
    with pytest.raises(UnitOfWorkStateError):
        other.begin(UnitOfWorkContext("different", "correlation"))
    created = uow()
    assert created.close().state is UnitOfWorkState.CLOSED


@pytest.mark.parametrize(
    ("factory", "match"),
    (
        (lambda: UnitOfWorkContext("", "c"), "unit_of_work_id"),
        (lambda: UnitOfWorkContext("u", ""), "correlation_id"),
        (
            lambda: UnitOfWorkRepository("x", object()),
            "CheckpointRepository",
        ),
        (
            lambda: UnitOfWorkOperation("x", "r", object()),
            "action",
        ),
        (
            lambda: UnitOfWorkOperation(
                "x", "r", lambda resource, context: None, object()
            ),
            "compensation",
        ),
        (
            lambda: UnitOfWorkResult(
                True,
                UnitOfWorkState.CREATED,
                "event",
                "u",
                INSTANT,
                error_code="bad",
                error_message="bad",
            ),
            "successful",
        ),
        (
            lambda: UnitOfWorkResult(
                False,
                UnitOfWorkState.FAILED,
                "event",
                "u",
                INSTANT,
            ),
            "failed result",
        ),
    ),
)
def test_model_validation(factory, match) -> None:
    with pytest.raises(UnitOfWorkValidationError, match=match):
        factory()


def test_validator_complete_surface() -> None:
    validator = UnitOfWorkValidator()
    context = UnitOfWorkContext("u", "c")
    repository = registration()
    item = operation()
    result = UnitOfWorkResult(
        True, UnitOfWorkState.CREATED, "event", "u", INSTANT
    )
    assert validator.validate_state("created") is UnitOfWorkState.CREATED
    assert validator.validate_context(context) is context
    assert validator.validate_repository(repository) is repository
    assert validator.validate_operation(item) is item
    assert validator.validate_result(result) is result
    assert validator.validate_repositories([repository]) == (repository,)
    with pytest.raises(UnitOfWorkValidationError):
        validator.validate_state("unknown")
    with pytest.raises(UnitOfWorkValidationError):
        validator.validate_context(object())
    with pytest.raises(UnitOfWorkValidationError, match="forbidden"):
        validator.validate_context(
            UnitOfWorkContext("u", "c", {"password": "x"})
        )
    with pytest.raises(UnitOfWorkRegistrationError):
        validator.validate_repository(object())
    with pytest.raises(UnitOfWorkValidationError):
        validator.validate_operation(object())
    with pytest.raises(UnitOfWorkValidationError):
        validator.validate_result(object())
    with pytest.raises(UnitOfWorkRegistrationError):
        validator.validate_repositories("invalid")
    with pytest.raises(UnitOfWorkRegistrationError):
        validator.validate_repositories([repository, repository])


def test_logging_events_are_structured(caplog) -> None:
    caplog.set_level(logging.INFO, logger="cko.core.uow")
    work = uow()
    repository = registration()
    work.register(repository)
    work.begin()
    work.commit()
    work.close()
    records = [
        record
        for record in caplog.records
        if record.name == "cko.core.uow"
    ]
    assert [record.event for record in records] == [
        "uow_created",
        "uow_registered",
        "uow_started",
        "uow_commit",
        "uow_closed",
    ]
    assert all(
        record.context["unit_of_work_id"] == "uow-1"
        for record in records
    )


def test_error_contract() -> None:
    error = UnitOfWorkExecutionError(
        "failed",
        unit_of_work_id="u",
        details={"operation": "x"},
    )
    assert error.to_dict() == {
        "code": "uow_execution_error",
        "unit_of_work_id": "u",
        "message": "failed",
        "details": {"operation": "x"},
    }
    for kwargs in (
        {"message": ""},
        {"message": "x", "code": ""},
        {"message": "x", "unit_of_work_id": ""},
        {"message": "x", "details": "bad"},
    ):
        with pytest.raises(ValueError):
            UnitOfWorkException(**kwargs)


def test_package_ast_utf8_and_forbidden_imports() -> None:
    package = (
        Path(__file__).parents[1] / "src" / "cko" / "core" / "uow"
    )
    forbidden = {
        "pathlib",
        "sqlite3",
        "cko.core.runtime",
        "cko.core.storage.filesystem",
        "cko.core.storage.sqlite",
    }
    for source_path in package.glob("*.py"):
        source = source_path.read_text(encoding="utf-8")
        assert "\ufffd" not in source
        tree = ast.parse(source, filename=str(source_path))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
        assert not any(
            imported == blocked or imported.startswith(f"{blocked}.")
            for imported in imports
            for blocked in forbidden
        )
        assert "TODO" not in source
