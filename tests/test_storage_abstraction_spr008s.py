"""Unit tests for the SPR-008S canonical storage abstraction."""

from __future__ import annotations

import ast
import json
import logging
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import MappingProxyType

import pytest

import cko.core as core
from cko.core.storage import (
    STORAGE_SCHEMA_VERSION,
    STORAGE_VERSION,
    Storage,
    StorageCapabilities,
    StorageContext,
    StorageDescriptor,
    StorageException,
    StorageFactory,
    StorageLocation,
    StorageMetadata,
    StorageObject,
    StorageOperation,
    StorageRegistry,
    StorageResult,
    StorageSession,
    StorageSessionState,
    StorageValidator,
)


NOW = datetime(2026, 7, 21, 12, 0, tzinfo=timezone.utc)


def metadata(**changes: object) -> StorageMetadata:
    values: dict[str, object] = {
        "name": "Canonical Storage",
        "description": "Technology-neutral test storage",
        "version": "1.2.3",
        "labels": {"tier": "logical", "nested": {"safe": True}},
    }
    values.update(changes)
    return StorageMetadata(**values)  # type: ignore[arg-type]


def capabilities(**changes: object) -> StorageCapabilities:
    values: dict[str, object] = {
        "operations": (
            StorageOperation.WRITE,
            StorageOperation.READ,
            StorageOperation.LIST,
        ),
        "supports_atomic_write": True,
    }
    values.update(changes)
    return StorageCapabilities(**values)  # type: ignore[arg-type]


def descriptor(
    identifier: str = "test.storage", **changes: object
) -> StorageDescriptor:
    values: dict[str, object] = {
        "identifier": identifier,
        "metadata": metadata(),
        "capabilities": capabilities(),
    }
    values.update(changes)
    return StorageDescriptor(**values)  # type: ignore[arg-type]


def location(**changes: object) -> StorageLocation:
    values: dict[str, object] = {
        "namespace": "knowledge",
        "key": "asset-001",
        "attributes": {"partition": "canonical"},
    }
    values.update(changes)
    return StorageLocation(**values)  # type: ignore[arg-type]


def storage_object(**changes: object) -> StorageObject:
    values: dict[str, object] = {
        "object_id": "object-001",
        "location": location(),
        "size": 42,
        "digest": "sha256:logical",
        "metadata": {"content_type": "application-neutral"},
    }
    values.update(changes)
    return StorageObject(**values)  # type: ignore[arg-type]


def context(**changes: object) -> StorageContext:
    values: dict[str, object] = {
        "correlation_id": "correlation-001",
        "operation": StorageOperation.READ,
        "location": location(),
        "parameters": {"limit": 10},
    }
    values.update(changes)
    return StorageContext(**values)  # type: ignore[arg-type]


def session(**changes: object) -> StorageSession:
    values: dict[str, object] = {
        "session_id": "session-001",
        "storage_id": "test.storage",
        "context": context(),
        "state": StorageSessionState.STARTED,
        "started_at": NOW,
    }
    values.update(changes)
    return StorageSession(**values)  # type: ignore[arg-type]


def result(**changes: object) -> StorageResult:
    values: dict[str, object] = {
        "storage_id": "test.storage",
        "operation": StorageOperation.READ,
        "success": True,
        "objects": (storage_object(),),
        "metadata": {"count": 1},
    }
    values.update(changes)
    return StorageResult(**values)  # type: ignore[arg-type]


class StubStorage(Storage):
    """In-memory test double that exercises contracts without persistence."""

    def __init__(self, public_descriptor: StorageDescriptor) -> None:
        self._descriptor = public_descriptor

    @property
    def descriptor(self) -> StorageDescriptor:
        return self._descriptor

    def execute(self, active_session: StorageSession) -> StorageResult:
        return StorageResult(
            storage_id=self.descriptor.identifier,
            operation=active_session.context.operation,
            success=True,
        )


def test_public_api_and_versions_are_exposed() -> None:
    expected = {
        "Storage", "StorageDescriptor", "StorageMetadata",
        "StorageCapabilities", "StorageContext", "StorageSession",
        "StorageResult", "StorageFactory", "StorageRegistry",
        "StorageValidator", "StorageException", "StorageLocation",
        "StorageObject", "StorageOperation",
    }
    assert expected.issubset(set(core.__all__))
    assert all(hasattr(core, name) for name in expected)
    assert STORAGE_SCHEMA_VERSION == "1.0"
    assert STORAGE_VERSION == "1.0.0"


@pytest.mark.parametrize(
    ("model", "model_type"),
    [
        (metadata(), StorageMetadata),
        (capabilities(), StorageCapabilities),
        (descriptor(), StorageDescriptor),
        (location(), StorageLocation),
        (storage_object(), StorageObject),
        (context(), StorageContext),
        (session(), StorageSession),
        (result(), StorageResult),
    ],
)
def test_all_models_round_trip_strict_json(model: object, model_type: type) -> None:
    payload = model.to_dict()  # type: ignore[attr-defined]
    encoded = model.to_json()  # type: ignore[attr-defined]
    assert payload["schema_version"] == STORAGE_SCHEMA_VERSION
    assert encoded == json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert model_type.from_dict(payload) == model
    assert model_type.from_json(encoded) == model


@pytest.mark.parametrize(
    "model",
    [
        metadata(), capabilities(), descriptor(), location(),
        storage_object(), context(), session(), result(),
    ],
)
def test_all_models_are_frozen(model: object) -> None:
    with pytest.raises((FrozenInstanceError, AttributeError)):
        model.schema_version = "2.0"  # type: ignore[attr-defined]


def test_nested_inputs_are_deeply_frozen_and_isolated() -> None:
    labels = {"nested": {"values": [1, 2]}}
    model = metadata(labels=labels)
    labels["nested"] = {"changed": True}
    assert isinstance(model.labels, MappingProxyType)
    nested = model.labels["nested"]
    assert isinstance(nested, MappingProxyType)
    assert nested["values"] == (1, 2)
    with pytest.raises(TypeError):
        model.labels["new"] = True  # type: ignore[index]


def test_capabilities_are_normalized_and_queryable() -> None:
    model = capabilities(
        operations=["write", StorageOperation.READ, StorageOperation.WRITE]
    )
    assert model.operations == (StorageOperation.READ, StorageOperation.WRITE)
    assert model.supports("read")
    assert not model.supports(StorageOperation.DELETE)
    with pytest.raises(StorageException, match="operation is invalid"):
        model.supports("invalid")


@pytest.mark.parametrize(
    "operation",
    [
        StorageOperation.READ, StorageOperation.WRITE, StorageOperation.DELETE,
        StorageOperation.LIST, StorageOperation.EXISTS,
        StorageOperation.METADATA,
    ],
)
def test_storage_operations_are_serializable(operation: StorageOperation) -> None:
    assert StorageOperation(operation.value) is operation
    assert isinstance(operation.value, str)


@pytest.mark.parametrize(
    "constructor",
    [
        lambda: metadata(name=" "),
        lambda: metadata(labels={"x": float("inf")}),
        lambda: metadata(labels={"x": object()}),
        lambda: capabilities(operations=()),
        lambda: capabilities(operations=("invalid",)),
        lambda: capabilities(supports_streaming=1),
        lambda: descriptor(metadata=object()),
        lambda: descriptor(capabilities=object()),
        lambda: location(key=" "),
        lambda: storage_object(location=object()),
        lambda: storage_object(size=-1),
        lambda: storage_object(size=True),
        lambda: context(operation="invalid"),
        lambda: context(location=object()),
        lambda: session(context=object()),
        lambda: session(started_at=datetime(2026, 7, 21)),
        lambda: result(success="yes"),
        lambda: result(objects=(object(),)),
        lambda: result(success=False),
    ],
)
def test_invalid_model_values_are_rejected(constructor) -> None:
    with pytest.raises(StorageException):
        constructor()


@pytest.mark.parametrize(
    ("model", "model_type"),
    [
        (metadata(), StorageMetadata),
        (capabilities(), StorageCapabilities),
        (descriptor(), StorageDescriptor),
        (location(), StorageLocation),
        (storage_object(), StorageObject),
        (context(), StorageContext),
        (session(), StorageSession),
        (result(), StorageResult),
    ],
)
def test_strict_envelopes_reject_changes(model: object, model_type: type) -> None:
    payload = model.to_dict()  # type: ignore[attr-defined]
    payload["unknown"] = True
    with pytest.raises(StorageException, match="envelope"):
        model_type.from_dict(payload)
    payload.pop("unknown")
    payload["schema_version"] = "9.0"
    with pytest.raises(StorageException, match="envelope"):
        model_type.from_dict(payload)


@pytest.mark.parametrize(
    "model_type",
    [
        StorageMetadata, StorageCapabilities, StorageDescriptor,
        StorageLocation, StorageObject, StorageContext, StorageSession,
        StorageResult,
    ],
)
def test_invalid_json_is_rejected(model_type: type) -> None:
    with pytest.raises(StorageException, match="JSON"):
        model_type.from_json("{")


def test_session_lifecycle_and_structured_events(caplog) -> None:
    caplog.set_level(logging.INFO)
    started = StorageSession.start(
        "session-001", "test.storage", context(), NOW
    )
    finished = started.finish(NOW + timedelta(seconds=1))
    failed = StorageSession.start(
        "session-002", "test.storage", context(), NOW
    ).finish(NOW + timedelta(seconds=2), failure="controlled failure")
    assert finished.state is StorageSessionState.FINISHED
    assert failed.state is StorageSessionState.FAILED
    assert failed.failure == "controlled failure"
    events = [getattr(record, "event", None) for record in caplog.records]
    assert events.count("storage_session_started") == 2
    assert events.count("storage_session_finished") == 2
    with pytest.raises(StorageException, match="only a started"):
        finished.finish(NOW + timedelta(seconds=3))


@pytest.mark.parametrize(
    "changes",
    [
        {"state": StorageSessionState.STARTED, "finished_at": NOW},
        {"state": StorageSessionState.FINISHED},
        {
            "state": StorageSessionState.FAILED,
            "finished_at": NOW,
            "failure": None,
        },
        {
            "state": StorageSessionState.FINISHED,
            "finished_at": NOW,
            "failure": "bad",
        },
        {
            "state": StorageSessionState.FINISHED,
            "finished_at": NOW - timedelta(seconds=1),
        },
    ],
)
def test_invalid_session_states_are_rejected(changes: dict[str, object]) -> None:
    with pytest.raises(StorageException):
        session(**changes)


def test_registry_is_instance_scoped_deterministic_and_read_only(caplog) -> None:
    caplog.set_level(logging.INFO)
    first = StorageRegistry()
    second = StorageRegistry()
    beta = descriptor("beta")
    alpha = descriptor("alpha")
    first.register(beta, lambda: StubStorage(beta))
    first.register(alpha, lambda: StubStorage(alpha))
    assert len(first) == 2
    assert len(second) == 0
    assert first.get(" alpha ") == alpha
    assert [item.identifier for item in first] == ["alpha", "beta"]
    assert list(first.snapshot()) == ["alpha", "beta"]
    assert first.constructor("beta")().descriptor == beta
    with pytest.raises(TypeError):
        first.snapshot()["gamma"] = descriptor("gamma")  # type: ignore[index]
    with pytest.raises(StorageException, match="already registered"):
        first.register(alpha, lambda: StubStorage(alpha))
    with pytest.raises(StorageException, match="not registered"):
        first.get("missing")
    with pytest.raises(StorageException, match="not registered"):
        first.constructor("missing")
    assert "storage_registered" in {
        getattr(record, "event", None) for record in caplog.records
    }


def test_registry_rejects_invalid_inputs() -> None:
    with pytest.raises(StorageException, match="validator"):
        StorageRegistry(validator=object())  # type: ignore[arg-type]
    registry = StorageRegistry()
    with pytest.raises(StorageException, match="callable"):
        registry.register(descriptor(), object())  # type: ignore[arg-type]
    with pytest.raises(StorageException, match="identifier"):
        registry.get(" ")


def test_factory_creates_and_validates_registered_storage(caplog) -> None:
    caplog.set_level(logging.INFO)
    registry = StorageRegistry()
    registered = descriptor()
    registry.register(registered, lambda: StubStorage(registered))
    storage = StorageFactory(registry).create(registered.identifier)
    produced = storage.execute(session())
    assert isinstance(storage, Storage)
    assert produced.success
    events = {getattr(record, "event", None) for record in caplog.records}
    assert {
        "storage_registered", "storage_created", "storage_validated",
    }.issubset(events)


def test_factory_rejects_invalid_composition_and_preserves_causes() -> None:
    with pytest.raises(StorageException, match="registry"):
        StorageFactory(object())  # type: ignore[arg-type]
    registry = StorageRegistry()
    with pytest.raises(StorageException, match="validator"):
        StorageFactory(registry, object())  # type: ignore[arg-type]
    registered = descriptor()
    registry.register(registered, lambda: object())  # type: ignore[arg-type]
    with pytest.raises(StorageException, match="did not create"):
        StorageFactory(registry).create(registered.identifier)

    failing_registry = StorageRegistry()

    def fail() -> Storage:
        raise RuntimeError("implementation failure")

    failing_registry.register(registered, fail)
    with pytest.raises(StorageException, match="construction failed") as caught:
        StorageFactory(failing_registry).create(registered.identifier)
    assert isinstance(caught.value.__cause__, RuntimeError)


def test_factory_rejects_descriptor_mismatch() -> None:
    registry = StorageRegistry()
    registered = descriptor()
    registry.register(registered, lambda: StubStorage(descriptor("other")))
    with pytest.raises(StorageException, match="does not match"):
        StorageFactory(registry).create(registered.identifier)


def test_validator_checks_every_required_contract() -> None:
    validator = StorageValidator()
    registered = descriptor()
    assert validator.validate_capabilities(registered.capabilities)
    assert validator.validate_descriptor(registered) == registered
    assert validator.validate_location(location())
    assert validator.validate_operation("read") is StorageOperation.READ
    assert validator.validate_context(context(), registered)
    assert validator.validate_session(session(), registered)
    storage = StubStorage(registered)
    assert validator.validate_storage(storage, registered) is storage


@pytest.mark.parametrize(
    "call",
    [
        lambda validator: validator.validate_capabilities(object()),
        lambda validator: validator.validate_descriptor(object()),
        lambda validator: validator.validate_descriptor(
            descriptor(contract_version="2.0.0")
        ),
        lambda validator: validator.validate_location(object()),
        lambda validator: validator.validate_operation("invalid"),
        lambda validator: validator.validate_operation(
            StorageOperation.DELETE, capabilities()
        ),
        lambda validator: validator.validate_context(object()),
        lambda validator: validator.validate_context(
            context(operation=StorageOperation.DELETE), descriptor()
        ),
        lambda validator: validator.validate_session(object()),
        lambda validator: validator.validate_session(
            session(storage_id="other"), descriptor()
        ),
        lambda validator: validator.validate_storage(object()),
    ],
)
def test_validator_rejects_invalid_contracts(call) -> None:
    with pytest.raises(StorageException):
        call(StorageValidator())


def test_exception_is_typed_serializable_and_validated() -> None:
    error = StorageException(
        "failure", code="failed", storage_id="storage", details={"x": 1}
    )
    assert error.to_dict() == {
        "code": "failed",
        "storage_id": "storage",
        "message": "failure",
        "details": {"x": 1},
    }
    with pytest.raises(ValueError, match="message"):
        StorageException(" ")
    with pytest.raises(ValueError, match="code"):
        StorageException("failure", code=" ")
    with pytest.raises(ValueError, match="storage_id"):
        StorageException("failure", storage_id=" ")
    with pytest.raises(ValueError, match="details"):
        StorageException("failure", details=object())  # type: ignore[arg-type]


def test_package_has_no_io_or_external_technology_imports() -> None:
    package = Path("src/cko/core/storage")
    forbidden_imports = {
        "boto3", "botocore", "google", "requests", "sqlalchemy", "sqlite3",
        "urllib", "http", "socket", "pathlib", "os", "shutil", "tempfile",
    }
    forbidden_calls = {"open", "exec", "eval", "compile", "__import__"}
    for source_file in package.glob("*.py"):
        tree = ast.parse(source_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".")[0] for alias in node.names}
                assert not roots & forbidden_imports
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden_imports
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_calls


def test_storage_contract_remains_abstract() -> None:
    with pytest.raises(TypeError):
        Storage()  # type: ignore[abstract]
