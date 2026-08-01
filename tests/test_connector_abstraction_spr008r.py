"""Unit tests for the SPR-008R connector abstraction foundation."""

from __future__ import annotations

import ast
import json
import logging
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import MappingProxyType

import pytest

import cko.core as public_core
from cko.core.connectors import (
    CONNECTOR_SCHEMA_VERSION,
    CONNECTOR_VERSION,
    Connector,
    ConnectorCapabilities,
    ConnectorContext,
    ConnectorDescriptor,
    ConnectorException,
    ConnectorFactory,
    ConnectorMetadata,
    ConnectorRegistry,
    ConnectorResult,
    ConnectorSession,
    ConnectorSessionState,
    ConnectorValidator,
)


NOW = datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc)


def metadata(**changes: object) -> ConnectorMetadata:
    values: dict[str, object] = {
        "name": "Memory Test Double",
        "description": "Technology-neutral test connector",
        "version": "1.2.3",
        "labels": {"tier": "test", "nested": [1, {"active": True}]},
    }
    values.update(changes)
    return ConnectorMetadata(**values)  # type: ignore[arg-type]


def capabilities(**changes: object) -> ConnectorCapabilities:
    values: dict[str, object] = {
        "operations": ("inspect", "list"),
        "features": ("batch",),
        "supports_streaming": False,
    }
    values.update(changes)
    return ConnectorCapabilities(**values)  # type: ignore[arg-type]


def descriptor(
    identifier: str = "test.memory", **changes: object
) -> ConnectorDescriptor:
    values: dict[str, object] = {
        "identifier": identifier,
        "metadata": metadata(),
        "capabilities": capabilities(),
    }
    values.update(changes)
    return ConnectorDescriptor(**values)  # type: ignore[arg-type]


def context(operation: str = "inspect", **changes: object) -> ConnectorContext:
    values: dict[str, object] = {
        "correlation_id": "corr-001",
        "operation": operation,
        "parameters": {"limit": 10, "filters": ["a", "b"]},
        "metadata": {"request": {"audited": True}},
    }
    values.update(changes)
    return ConnectorContext(**values)  # type: ignore[arg-type]


def session(
    connector_id: str = "test.memory", **changes: object
) -> ConnectorSession:
    values: dict[str, object] = {
        "session_id": "session-001",
        "connector_id": connector_id,
        "context": context(),
        "state": ConnectorSessionState.STARTED,
        "started_at": NOW,
    }
    values.update(changes)
    return ConnectorSession(**values)  # type: ignore[arg-type]


class StubConnector(Connector):
    """In-memory test double used only to exercise the canonical port."""

    def __init__(self, value: ConnectorDescriptor | None = None) -> None:
        self._descriptor = value or descriptor()

    @property
    def descriptor(self) -> ConnectorDescriptor:
        return self._descriptor

    def execute(self, active_session: ConnectorSession) -> ConnectorResult:
        return ConnectorResult(
            session_id=active_session.session_id,
            connector_id=active_session.connector_id,
            success=True,
            data={"accepted": True},
        )


def test_public_api_and_versions_are_exposed() -> None:
    expected = {
        "Connector", "ConnectorDescriptor", "ConnectorMetadata",
        "ConnectorCapabilities", "ConnectorContext", "ConnectorSession",
        "ConnectorResult", "ConnectorFactory", "ConnectorRegistry",
        "ConnectorValidator", "ConnectorException",
    }
    assert CONNECTOR_SCHEMA_VERSION == "1.0"
    assert CONNECTOR_VERSION == "1.0.0"
    assert expected.issubset(set(public_core.__all__))
    assert all(hasattr(public_core, name) for name in expected)


@pytest.mark.parametrize(
    "model",
    [
        metadata(),
        capabilities(),
        descriptor(),
        context(),
        session(),
        ConnectorResult(
            "session-001", "test.memory", True, {"count": 1}, (), {"x": 2}
        ),
    ],
)
def test_models_are_strictly_serializable_and_deterministic(model: object) -> None:
    model_type = type(model)
    payload = model.to_dict()  # type: ignore[attr-defined]
    encoded = model.to_json()  # type: ignore[attr-defined]
    assert json.loads(encoded) == payload
    assert encoded == model.to_json()  # type: ignore[attr-defined]
    assert model_type.from_dict(payload) == model
    assert model_type.from_json(encoded) == model
    assert payload["schema_version"] == CONNECTOR_SCHEMA_VERSION


def test_models_are_deeply_immutable_and_detached_from_inputs() -> None:
    labels = {"nested": [1, {"active": True}]}
    item = metadata(labels=labels)
    labels["nested"].append(2)  # type: ignore[union-attr]
    assert item.labels["nested"] == (1, MappingProxyType({"active": True}))
    with pytest.raises(TypeError):
        item.labels["new"] = "value"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        item.name = "changed"  # type: ignore[misc]


def test_capabilities_normalize_order_and_answer_support() -> None:
    item = capabilities(
        operations=("list", "inspect", "list"),
        features={"zeta", "alpha"},
        supports_streaming=True,
    )
    assert item.operations == ("inspect", "list")
    assert item.features == ("alpha", "zeta")
    assert item.supports("inspect")
    assert not item.supports("write")


@pytest.mark.parametrize(
    ("builder", "message"),
    [
        (lambda: metadata(name=" "), "name"),
        (lambda: metadata(labels={"x": float("inf")}), "finite"),
        (lambda: capabilities(operations=()), "operations"),
        (lambda: capabilities(operations="inspect"), "collection"),
        (lambda: capabilities(supports_streaming=1), "boolean"),
        (lambda: descriptor(metadata="bad"), "ConnectorMetadata"),
        (lambda: descriptor(capabilities="bad"), "ConnectorCapabilities"),
        (lambda: context(parameters={"x": object()}), "unsupported"),
        (
            lambda: ConnectorResult("s", "c", True, errors=("failure",)),
            "successful",
        ),
        (lambda: ConnectorResult("s", "c", False), "requires errors"),
    ],
)
def test_invalid_model_values_are_rejected(builder: object, message: str) -> None:
    with pytest.raises(ConnectorException, match=message):
        builder()  # type: ignore[operator]


@pytest.mark.parametrize(
    "model",
    [metadata(), capabilities(), descriptor(), context(), session()],
)
def test_unknown_or_unsupported_envelopes_are_rejected(model: object) -> None:
    payload = model.to_dict()  # type: ignore[attr-defined]
    payload["unknown"] = True
    with pytest.raises(ConnectorException, match="envelope"):
        type(model).from_dict(payload)
    payload.pop("unknown")
    payload["schema_version"] = "9.0"
    with pytest.raises(ConnectorException, match="envelope"):
        type(model).from_dict(payload)
    with pytest.raises(ConnectorException, match="JSON"):
        type(model).from_json("{")


def test_session_lifecycle_is_immutable_and_structurally_valid(caplog) -> None:
    caplog.set_level(logging.INFO, logger="cko.core.connectors.session")
    started = ConnectorSession.start(
        "session-001", "test.memory", context(), NOW
    )
    finished = started.finish(NOW + timedelta(seconds=1))
    failed = session(session_id="session-002").finish(
        NOW + timedelta(seconds=2), failure="controlled failure"
    )
    assert started.state is ConnectorSessionState.STARTED
    assert finished.state is ConnectorSessionState.FINISHED
    assert failed.state is ConnectorSessionState.FAILED
    assert failed.failure == "controlled failure"
    assert [record.event for record in caplog.records] == [
        "connector_session_started",
        "connector_session_finished",
        "connector_session_finished",
    ]
    with pytest.raises(ConnectorException, match="only a started"):
        finished.finish(NOW + timedelta(seconds=3))


@pytest.mark.parametrize(
    "changes",
    [
        {"state": ConnectorSessionState.STARTED, "finished_at": NOW},
        {"state": ConnectorSessionState.FINISHED},
        {
            "state": ConnectorSessionState.FAILED,
            "finished_at": NOW,
            "failure": None,
        },
        {
            "state": ConnectorSessionState.FINISHED,
            "finished_at": NOW,
            "failure": "bad",
        },
        {
            "state": ConnectorSessionState.FINISHED,
            "finished_at": NOW - timedelta(seconds=1),
        },
    ],
)
def test_invalid_session_states_are_rejected(changes: dict[str, object]) -> None:
    with pytest.raises(ConnectorException):
        session(**changes)


def test_registry_prevents_duplicates_and_enumerates_deterministically(
    caplog,
) -> None:
    caplog.set_level(logging.INFO, logger="cko.core.connectors")
    registry = ConnectorRegistry()
    beta = descriptor("beta")
    alpha = descriptor("alpha")
    registry.register(beta, lambda: StubConnector(beta))
    registry.register(alpha, lambda: StubConnector(alpha))
    assert len(registry) == 2
    assert registry.get(" alpha ") == alpha
    assert [item.identifier for item in registry] == ["alpha", "beta"]
    assert list(registry.snapshot()) == ["alpha", "beta"]
    assert registry.constructor("beta")().descriptor == beta
    with pytest.raises(TypeError):
        registry.snapshot()["gamma"] = descriptor("gamma")  # type: ignore[index]
    with pytest.raises(ConnectorException, match="already registered"):
        registry.register(alpha, lambda: StubConnector(alpha))
    with pytest.raises(ConnectorException, match="not registered"):
        registry.get("missing")
    with pytest.raises(ConnectorException, match="not registered"):
        registry.constructor("missing")
    assert "connector_registered" in {
        getattr(record, "event", None) for record in caplog.records
    }


def test_registry_rejects_invalid_inputs() -> None:
    with pytest.raises(ConnectorException, match="validator"):
        ConnectorRegistry(validator=object())  # type: ignore[arg-type]
    registry = ConnectorRegistry()
    with pytest.raises(ConnectorException, match="callable"):
        registry.register(descriptor(), object())  # type: ignore[arg-type]
    with pytest.raises(ConnectorException, match="identifier"):
        registry.get(" ")


def test_factory_creates_and_validates_registered_connector(caplog) -> None:
    caplog.set_level(logging.INFO, logger="cko.core.connectors")
    registry = ConnectorRegistry()
    registered = descriptor()
    registry.register(registered, lambda: StubConnector(registered))
    connector = ConnectorFactory(registry).create(registered.identifier)
    active = session()
    result = connector.execute(active)
    assert isinstance(connector, Connector)
    assert result.success
    assert result.connector_id == registered.identifier
    events = {getattr(record, "event", None) for record in caplog.records}
    assert {
        "connector_registered", "connector_created", "connector_validated",
    }.issubset(events)


def test_factory_rejects_bad_registry_validator_instance_and_constructor() -> None:
    with pytest.raises(ConnectorException, match="registry"):
        ConnectorFactory(object())  # type: ignore[arg-type]
    registry = ConnectorRegistry()
    with pytest.raises(ConnectorException, match="validator"):
        ConnectorFactory(registry, object())  # type: ignore[arg-type]
    registered = descriptor()
    registry.register(registered, lambda: object())  # type: ignore[arg-type]
    with pytest.raises(ConnectorException, match="did not create"):
        ConnectorFactory(registry).create(registered.identifier)


def test_factory_rejects_descriptor_mismatch_and_preserves_failure_cause() -> None:
    registered = descriptor()
    registry = ConnectorRegistry()
    registry.register(registered, lambda: StubConnector(descriptor("other")))
    with pytest.raises(ConnectorException, match="does not match"):
        ConnectorFactory(registry).create(registered.identifier)

    failing_registry = ConnectorRegistry()

    def fail() -> Connector:
        raise RuntimeError("implementation failure")

    failing_registry.register(registered, fail)
    with pytest.raises(ConnectorException, match="construction failed") as caught:
        ConnectorFactory(failing_registry).create(registered.identifier)
    assert isinstance(caught.value.__cause__, RuntimeError)


def test_validator_checks_all_public_contracts() -> None:
    validator = ConnectorValidator()
    registered = descriptor()
    active_context = context()
    active_session = session()
    connector = StubConnector(registered)
    assert validator.validate_capabilities(registered.capabilities)
    assert validator.validate_descriptor(registered) == registered
    assert validator.validate_context(active_context, registered) == active_context
    assert validator.validate_session(active_session, registered) == active_session
    assert validator.validate_connector(connector, registered) is connector


def test_validator_rejects_wrong_types_versions_operations_and_bindings() -> None:
    validator = ConnectorValidator()
    registered = descriptor()
    with pytest.raises(ConnectorException, match="ConnectorCapabilities"):
        validator.validate_capabilities(object())  # type: ignore[arg-type]
    with pytest.raises(ConnectorException, match="ConnectorDescriptor"):
        validator.validate_descriptor(object())  # type: ignore[arg-type]
    with pytest.raises(ConnectorException, match="contract version"):
        validator.validate_descriptor(
            descriptor(contract_version="2.0.0")
        )
    with pytest.raises(ConnectorException, match="ConnectorContext"):
        validator.validate_context(object())  # type: ignore[arg-type]
    with pytest.raises(ConnectorException, match="unsupported"):
        validator.validate_context(context("delete"), registered)
    with pytest.raises(ConnectorException, match="ConnectorSession"):
        validator.validate_session(object())  # type: ignore[arg-type]
    with pytest.raises(ConnectorException, match="does not match"):
        validator.validate_session(session("other"), registered)
    with pytest.raises(ConnectorException, match="did not create"):
        validator.validate_connector(object())  # type: ignore[arg-type]


def test_exception_is_typed_serializable_and_validated() -> None:
    error = ConnectorException(
        "failure", code="failed", connector_id="connector", details={"x": 1}
    )
    assert isinstance(error, Exception)
    assert error.to_dict() == {
        "code": "failed",
        "connector_id": "connector",
        "message": "failure",
        "details": {"x": 1},
    }
    with pytest.raises(ValueError, match="message"):
        ConnectorException(" ")
    with pytest.raises(ValueError, match="code"):
        ConnectorException("failure", code=" ")
    with pytest.raises(ValueError, match="connector_id"):
        ConnectorException("failure", connector_id=" ")


def test_package_has_no_external_technology_or_dependency_imports() -> None:
    package = Path("src/cko/core/connectors")
    forbidden_imports = {
        "boto3", "botocore", "google", "requests", "sqlalchemy",
        "sqlite3", "urllib", "http", "socket", "pathlib", "os",
    }
    forbidden_calls = {"open", "exec", "eval", "compile", "__import__"}
    for source_file in package.glob("*.py"):
        tree = ast.parse(source_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not {alias.name.split(".")[0]
                            for alias in node.names} & forbidden_imports
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden_imports
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_calls


def test_connector_contract_remains_abstract() -> None:
    with pytest.raises(TypeError):
        Connector()  # type: ignore[abstract]
