"""Complete verification suite for SPR-008U SQLite Storage Adapter."""

from __future__ import annotations

import base64
import json
import logging
import sqlite3
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path

import pytest

from cko.core.connectors import (
    Connector,
    ConnectorContext,
    ConnectorRegistry,
    ConnectorSession,
)
from cko.core.storage import (
    Storage,
    StorageContext,
    StorageException,
    StorageLocation,
    StorageOperation,
    StorageRegistry,
    StorageSession,
)
from cko.core.storage.sqlite import (
    SQLITE_IDENTIFIER,
    SQLITE_OPERATIONS,
    SQLITE_SCHEMA_VERSION,
    SQLITE_VERSION,
    SQLiteConnector,
    SQLiteDescriptor,
    SQLiteLocationResolver,
    SQLiteResult,
    SQLiteSession,
    SQLiteStorage,
    SQLiteStorageFactory,
    SQLiteStorageValidator,
)


def location(namespace: str = "documents", key: str = "item") -> StorageLocation:
    return StorageLocation(namespace=namespace, key=key)


def storage_session(
    operation: StorageOperation,
    target: StorageLocation | None = None,
    parameters: dict[str, object] | None = None,
    *,
    session_id: str = "storage-session",
) -> StorageSession:
    context = StorageContext(
        correlation_id=f"correlation-{session_id}",
        operation=operation,
        location=target or location(),
        parameters=parameters or {},
    )
    return StorageSession.start(
        session_id,
        SQLITE_IDENTIFIER,
        context,
        datetime.now(UTC),
    )


def connector_session(
    operation: str,
    target: StorageLocation | None = None,
    parameters: dict[str, object] | None = None,
    *,
    session_id: str = "connector-session",
) -> ConnectorSession:
    values = dict(parameters or {})
    values["location"] = (target or location()).to_dict()
    return ConnectorSession.start(
        session_id,
        SQLITE_IDENTIFIER,
        ConnectorContext(
            correlation_id=f"correlation-{session_id}",
            operation=operation,
            parameters=values,
        ),
        datetime.now(UTC),
    )


@pytest.fixture
def storage(tmp_path: Path) -> SQLiteStorage:
    return SQLiteStorage(tmp_path / "adapter.sqlite3")


def test_public_api_and_descriptor_contracts() -> None:
    descriptor = SQLiteDescriptor()
    assert SQLITE_SCHEMA_VERSION == "1.0"
    assert SQLITE_VERSION == "1.0.0"
    assert descriptor.storage.identifier == SQLITE_IDENTIFIER
    assert descriptor.connector.identifier == SQLITE_IDENTIFIER
    assert descriptor.connector.capabilities.operations == SQLITE_OPERATIONS
    assert descriptor.storage.capabilities.supports_transactions
    assert descriptor.storage.capabilities.supports_atomic_write
    assert isinstance(SQLiteStorage, type)
    assert issubclass(SQLiteStorage, Storage)
    assert issubclass(SQLiteConnector, Connector)
    with pytest.raises(FrozenInstanceError):
        descriptor.schema_version = "2.0"  # type: ignore[misc]


def test_descriptor_serialization_is_deterministic() -> None:
    descriptor = SQLiteDescriptor()
    payload = descriptor.to_json()
    assert payload == descriptor.to_json()
    assert SQLiteDescriptor.from_json(payload) == descriptor
    assert SQLiteDescriptor.from_dict(descriptor.to_dict()) == descriptor
    assert payload == json.dumps(
        json.loads(payload),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def test_create_read_and_metadata(storage: SQLiteStorage) -> None:
    created = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            parameters={
                "sqlite_operation": "create",
                "value": {"z": 1, "a": ["ç", True]},
                "metadata": {"origin": "test"},
            },
        )
    )
    assert created.success
    assert created.objects[0].object_id == "documents:item"
    assert created.objects[0].metadata["value_metadata"]["origin"] == "test"
    read = storage.execute(storage_session(StorageOperation.READ))
    assert read.success
    assert dict(read.metadata["value"]) == {"a": ("ç", True), "z": 1}
    assert read.metadata["serialized_value"] == (
        '{"kind":"json","value":{"a":["ç",true],"z":1}}'
    )
    metadata = storage.execute(storage_session(StorageOperation.METADATA))
    assert metadata.success
    assert metadata.objects[0].digest == created.objects[0].digest
    duplicate = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            parameters={"sqlite_operation": "create", "value": "duplicate"},
        )
    )
    assert not duplicate.success
    assert "UNIQUE constraint failed" in duplicate.message


def test_write_upsert_and_binary_round_trip(storage: SQLiteStorage) -> None:
    first = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            parameters={"value": {"version": 1}},
        )
    )
    second = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            parameters={"value": {"version": 2}},
        )
    )
    assert first.success and second.success
    assert first.objects[0].digest != second.objects[0].digest
    binary = b"\x00CKO\xff"
    written = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            location("binary", "blob"),
            {"content_base64": base64.b64encode(binary).decode("ascii")},
        )
    )
    assert written.success
    read = storage.execute(
        storage_session(StorageOperation.READ, location("binary", "blob"))
    )
    assert base64.b64decode(read.metadata["content_base64"]) == binary


def test_exists_delete_and_missing_object(storage: SQLiteStorage) -> None:
    absent = storage.execute(storage_session(StorageOperation.EXISTS))
    assert absent.success and absent.metadata["exists"] is False
    missing = storage.execute(storage_session(StorageOperation.READ))
    assert not missing.success
    assert "does not exist" in missing.message
    storage.execute(
        storage_session(StorageOperation.WRITE, parameters={"value": 42})
    )
    present = storage.execute(storage_session(StorageOperation.EXISTS))
    assert present.metadata["exists"] is True
    deleted = storage.execute(storage_session(StorageOperation.DELETE))
    assert deleted.success and deleted.objects[0].object_id == "documents:item"
    again = storage.execute(storage_session(StorageOperation.DELETE))
    assert not again.success


def test_list_is_deterministic_and_prefix_scoped(storage: SQLiteStorage) -> None:
    for key in ("folder/z", "folder/a", "other", "folder/nested/b"):
        result = storage.execute(
            storage_session(
                StorageOperation.WRITE,
                location("documents", key),
                {"value": key},
                session_id=f"write-{key}",
            )
        )
        assert result.success
    all_rows = storage.execute(
        storage_session(StorageOperation.LIST, location("documents", "."))
    )
    assert [item.location.key for item in all_rows.objects] == [
        "folder/a",
        "folder/nested/b",
        "folder/z",
        "other",
    ]
    prefix = storage.execute(
        storage_session(StorageOperation.LIST, location("documents", "folder"))
    )
    assert [item.location.key for item in prefix.objects] == [
        "folder/a",
        "folder/nested/b",
        "folder/z",
    ]
    assert prefix.metadata["count"] == 3


def test_copy_and_move_are_atomic(storage: SQLiteStorage) -> None:
    source = location("source", "one")
    copied = location("target", "copy")
    moved = location("target", "move")
    storage.execute(
        storage_session(
            StorageOperation.WRITE,
            source,
            {"value": {"id": 1}},
        )
    )
    copy_result = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            source,
            {"sqlite_operation": "copy", "target": copied.to_dict()},
        )
    )
    assert copy_result.success
    move_result = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            source,
            {"sqlite_operation": "move", "target": moved.to_dict()},
        )
    )
    assert move_result.success
    assert storage.execute(
        storage_session(StorageOperation.EXISTS, source)
    ).metadata["exists"] is False
    assert storage.execute(
        storage_session(StorageOperation.READ, copied)
    ).metadata["value"] == {"id": 1}
    assert storage.execute(
        storage_session(StorageOperation.READ, moved)
    ).metadata["value"] == {"id": 1}


def test_connector_executes_all_operations(tmp_path: Path) -> None:
    connector = SQLiteConnector(tmp_path / "connector.sqlite3")
    first = location("connector", "first")
    second = location("connector", "second")
    third = location("connector", "third")
    requests = (
        connector_session("create", first, {"value": {"x": 1}}, session_id="c1"),
        connector_session("read", first, session_id="c2"),
        connector_session("write", first, {"value": {"x": 2}}, session_id="c3"),
        connector_session("exists", first, session_id="c4"),
        connector_session("metadata", first, session_id="c5"),
        connector_session("list", location("connector", "."), session_id="c6"),
        connector_session(
            "copy",
            first,
            {"target": second.to_dict()},
            session_id="c7",
        ),
        connector_session(
            "move",
            second,
            {"target": third.to_dict()},
            session_id="c8",
        ),
        connector_session("delete", first, session_id="c9"),
    )
    results = [connector.execute(request) for request in requests]
    assert all(result.success for result in results)
    assert results[1].data["storage_result"]["metadata"]["value"] == {"x": 1}


def test_connector_failures_are_typed_results(tmp_path: Path) -> None:
    connector = SQLiteConnector(tmp_path / "errors.sqlite3")
    bad_operation = connector.execute(connector_session("unsupported"))
    assert not bad_operation.success
    assert "unsupported" in bad_operation.errors[0]
    missing = ConnectorSession.start(
        "missing-location",
        SQLITE_IDENTIFIER,
        ConnectorContext(
            correlation_id="correlation",
            operation="read",
        ),
        datetime.now(UTC),
    )
    result = connector.execute(missing)
    assert not result.success
    assert "requires location" in result.errors[0]


def test_explicit_transaction_commit(tmp_path: Path) -> None:
    database = tmp_path / "commit.sqlite3"
    storage = SQLiteStorage(database)
    bridge = SQLiteSession.from_connector(
        connector_session(
            "write",
            parameters={"value": "committed"},
            session_id="commit",
        ),
        storage,
    )
    with bridge:
        result = bridge.execute()
        assert result.success
        assert bridge._active
    observer = SQLiteStorage(database)
    assert observer.execute(
        storage_session(StorageOperation.READ)
    ).metadata["value"] == "committed"


def test_explicit_transaction_manual_rollback(tmp_path: Path) -> None:
    database = tmp_path / "rollback.sqlite3"
    storage = SQLiteStorage(database)
    bridge = SQLiteSession.from_connector(
        connector_session(
            "write",
            parameters={"value": "discarded"},
            session_id="rollback",
        ),
        storage,
    )
    with bridge:
        assert bridge.execute().success
        bridge.rollback()
    observer = SQLiteStorage(database)
    assert observer.execute(
        storage_session(StorageOperation.EXISTS)
    ).metadata["exists"] is False


def test_failed_explicit_transaction_rolls_back_all_work(
    tmp_path: Path,
) -> None:
    database = tmp_path / "failed-transaction.sqlite3"
    storage = SQLiteStorage(database)
    bridge = SQLiteSession.from_connector(
        connector_session(
            "write",
            parameters={"value": "first"},
            session_id="failed",
        ),
        storage,
    )
    with bridge:
        assert bridge.execute().success
        duplicate = storage_session(
            StorageOperation.WRITE,
            parameters={"sqlite_operation": "create", "value": "duplicate"},
            session_id="duplicate",
        )
        assert not bridge.execute(duplicate).success
    observer = SQLiteStorage(database)
    assert observer.execute(
        storage_session(StorageOperation.EXISTS)
    ).metadata["exists"] is False


def test_session_isolation_between_connections(tmp_path: Path) -> None:
    database = tmp_path / "isolation.sqlite3"
    writer = SQLiteStorage(database)
    reader = SQLiteStorage(database)
    bridge = SQLiteSession.from_connector(
        connector_session(
            "write",
            parameters={"value": "uncommitted"},
            session_id="isolation",
        ),
        writer,
    )
    with bridge:
        assert bridge.execute().success
        unseen = reader.execute(storage_session(StorageOperation.EXISTS))
        assert unseen.success
        assert unseen.metadata["exists"] is False
    seen = reader.execute(storage_session(StorageOperation.EXISTS))
    assert seen.metadata["exists"] is True


def test_prepared_statements_prevent_key_injection(storage: SQLiteStorage) -> None:
    hostile = location("documents", "' OR 1=1 --")
    normal = location("documents", "normal")
    storage.execute(
        storage_session(
            StorageOperation.WRITE,
            hostile,
            {"value": "hostile"},
        )
    )
    storage.execute(
        storage_session(
            StorageOperation.WRITE,
            normal,
            {"value": "normal"},
        )
    )
    assert storage.execute(
        storage_session(StorageOperation.READ, hostile)
    ).metadata["value"] == "hostile"
    assert len(storage.execute(
        storage_session(StorageOperation.LIST, location("documents", "."))
    ).objects) == 2


def test_factory_and_registries_compose_public_contracts(
    tmp_path: Path,
) -> None:
    factory = SQLiteStorageFactory(tmp_path / "factory.sqlite3")
    storage = factory.create_storage()
    connector = factory.create_connector()
    assert isinstance(storage, SQLiteStorage)
    assert isinstance(connector, SQLiteConnector)
    storage_registry = StorageRegistry()
    storage_registry.register(factory.descriptor.storage, factory.create_storage)
    connector_registry = ConnectorRegistry()
    connector_registry.register(
        factory.descriptor.connector,
        factory.create_connector,
    )
    assert storage_registry.get(SQLITE_IDENTIFIER) == factory.descriptor.storage
    assert (
        connector_registry.get(SQLITE_IDENTIFIER)
        == factory.descriptor.connector
    )


def test_validator_accepts_valid_composition(tmp_path: Path) -> None:
    validator = SQLiteStorageValidator()
    descriptor = validator.validate_descriptor(SQLiteDescriptor())
    resolver = validator.validate_database(tmp_path / "validated.sqlite3")
    bridge = SQLiteSession.from_connector(connector_session("exists"))
    result = SQLiteResult.from_storage(
        bridge,
        SQLiteStorage(tmp_path / "result.sqlite3").execute(
            bridge.storage_session
        ),
    )
    assert resolver.database.is_absolute()
    assert validator.validate_session(bridge, descriptor) is bridge
    assert validator.validate_result(result) is result


def test_session_and_result_serialization_round_trip(tmp_path: Path) -> None:
    bridge = SQLiteSession.from_connector(connector_session("exists"))
    restored = SQLiteSession.from_json(bridge.to_json())
    assert restored.to_dict() == bridge.to_dict()
    result = SQLiteStorage(tmp_path / "round-trip.sqlite3").execute(
        bridge.storage_session
    )
    paired = SQLiteResult.from_storage(bridge, result)
    assert SQLiteResult.from_json(paired.to_json()) == paired
    assert paired.to_json() == paired.to_json()


def test_deterministic_serialization_rejects_unsupported_values(
    storage: SQLiteStorage,
) -> None:
    with pytest.raises(StorageException, match="unsupported serializable value"):
        storage_session(
            StorageOperation.WRITE,
            parameters={"value": {1, 2, 3}},
        )
    with pytest.raises(StorageException, match="finite"):
        storage_session(
            StorageOperation.WRITE,
            parameters={"value": float("nan")},
        )
    conflicting = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            parameters={"value": 1, "content": "two"},
        )
    )
    assert not conflicting.success


def test_database_is_created_when_missing(tmp_path: Path) -> None:
    database = tmp_path / "missing" / "created.sqlite3"
    assert not database.exists()
    storage = SQLiteStorage(database)
    assert database.is_file()
    assert storage.execute(
        storage_session(StorageOperation.EXISTS)
    ).success


def test_corrupt_database_raises_typed_exception(tmp_path: Path) -> None:
    database = tmp_path / "corrupt.sqlite3"
    database.write_bytes(b"this is not a SQLite database")
    with pytest.raises(StorageException) as captured:
        SQLiteStorage(database)
    assert captured.value.code == "sqlite_database_error"
    assert "SQLite database error" in str(captured.value)


def test_context_manager_closes_storage(tmp_path: Path) -> None:
    with SQLiteStorage(tmp_path / "context.sqlite3") as storage:
        assert storage.execute(
            storage_session(StorageOperation.EXISTS)
        ).success
    with pytest.raises(StorageException, match="closed"):
        storage.execute(storage_session(StorageOperation.EXISTS))


def test_required_structured_logging_events(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="cko.core.storage.sqlite")
    database = tmp_path / "logging.sqlite3"
    storage = SQLiteStorage(database)
    storage.execute(
        storage_session(StorageOperation.WRITE, parameters={"value": 1})
    )
    storage.execute(storage_session(StorageOperation.READ))
    storage.execute(storage_session(StorageOperation.EXISTS))
    storage.execute(storage_session(StorageOperation.METADATA))
    storage.execute(
        storage_session(StorageOperation.LIST, location("documents", "."))
    )
    storage.execute(storage_session(StorageOperation.DELETE))
    bridge = SQLiteSession.from_connector(
        connector_session(
            "write",
            parameters={"value": 2},
            session_id="logging-rollback",
        ),
        storage,
    )
    with bridge:
        bridge.execute()
        bridge.rollback()
    storage.close()
    events = {getattr(record, "event", None) for record in caplog.records}
    assert {
        "sqlite_open",
        "sqlite_close",
        "sqlite_begin",
        "sqlite_commit",
        "sqlite_rollback",
        "sqlite_read",
        "sqlite_write",
        "sqlite_delete",
        "sqlite_list",
        "sqlite_exists",
        "sqlite_metadata",
    } <= events
    for record in caplog.records:
        if getattr(record, "event", "").startswith("sqlite_"):
            assert isinstance(getattr(record, "context"), dict)


def test_simulated_logical_concurrency_last_committed_write_wins(
    tmp_path: Path,
) -> None:
    database = tmp_path / "concurrency.sqlite3"
    first = SQLiteStorage(database)
    second = SQLiteStorage(database)
    assert first.execute(
        storage_session(
            StorageOperation.WRITE,
            parameters={"value": {"writer": 1}},
            session_id="writer-1",
        )
    ).success
    assert second.execute(
        storage_session(
            StorageOperation.WRITE,
            parameters={"value": {"writer": 2}},
            session_id="writer-2",
        )
    ).success
    observed = first.execute(storage_session(StorageOperation.READ))
    assert observed.metadata["value"] == {"writer": 2}


def test_invalid_composition_and_operations_are_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(StorageException):
        SQLiteStorageValidator(storage_validator=object())  # type: ignore[arg-type]
    with pytest.raises(StorageException):
        SQLiteStorageFactory(
            tmp_path / "invalid.sqlite3",
            validator=object(),  # type: ignore[arg-type]
        )
    with pytest.raises(StorageException):
        SQLiteLocationResolver(tmp_path)
    storage = SQLiteStorage(tmp_path / "operations.sqlite3")
    incompatible = storage.execute(
        storage_session(
            StorageOperation.READ,
            parameters={"sqlite_operation": "write", "value": 1},
        )
    )
    assert not incompatible.success
    unsupported = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            parameters={"sqlite_operation": "vacuum"},
        )
    )
    assert not unsupported.success


def test_package_has_no_runtime_or_external_dependency() -> None:
    package = (
        Path(__file__).parents[1]
        / "src"
        / "cko"
        / "core"
        / "storage"
        / "sqlite"
    )
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in package.glob("*.py")
    )
    assert "cko.core.runtime" not in source
    assert "sqlalchemy" not in source.lower()
    assert "import sqlite3" in source
    assert "execute(" in source
    with sqlite3.connect(":memory:") as connection:
        assert connection.execute("SELECT sqlite_version()").fetchone()


def test_strict_adapter_envelopes_and_json_are_rejected(
    tmp_path: Path,
) -> None:
    bridge = SQLiteSession.from_connector(connector_session("exists"))
    storage_result = SQLiteStorage(tmp_path / "strict.sqlite3").execute(
        bridge.storage_session
    )
    paired = SQLiteResult.from_storage(bridge, storage_result)
    models = (SQLiteDescriptor, SQLiteSession, SQLiteResult)
    for model in models:
        with pytest.raises(StorageException):
            model.from_dict({})
        with pytest.raises(StorageException):
            model.from_json("{")
        with pytest.raises(StorageException):
            model.from_json("[]")
    invalid_descriptor = SQLiteDescriptor().to_dict()
    invalid_descriptor["model"] = "wrong"
    with pytest.raises(StorageException):
        SQLiteDescriptor.from_dict(invalid_descriptor)
    invalid_session = bridge.to_dict()
    invalid_session["connector_session"] = "wrong"
    with pytest.raises(StorageException):
        SQLiteSession.from_dict(invalid_session)
    invalid_result = paired.to_dict()
    invalid_result["storage_result"] = "wrong"
    with pytest.raises(StorageException):
        SQLiteResult.from_dict(invalid_result)
    with pytest.raises(StorageException):
        SQLiteResult.from_storage(object(), storage_result)
    with pytest.raises(StorageException):
        SQLiteResult.from_storage(bridge, object())  # type: ignore[arg-type]


def test_resolver_session_and_validator_error_paths(tmp_path: Path) -> None:
    with pytest.raises(StorageException):
        SQLiteLocationResolver("")
    resolver = SQLiteLocationResolver(tmp_path / "resolver.sqlite3")
    with pytest.raises(StorageException):
        resolver.resolve(object())  # type: ignore[arg-type]
    with pytest.raises(StorageException, match="null"):
        resolver.resolve(StorageLocation(namespace="bad\x00space", key="key"))
    bridge = SQLiteSession.from_connector(connector_session("exists"))
    with pytest.raises(StorageException, match="not bound"):
        bridge.__enter__()
    with pytest.raises(StorageException, match="not bound"):
        bridge.execute()
    with pytest.raises(StorageException):
        bridge.bind(object())  # type: ignore[arg-type]
    validator = SQLiteStorageValidator()
    with pytest.raises(StorageException):
        validator.validate_descriptor(object())  # type: ignore[arg-type]
    with pytest.raises(StorageException):
        validator.validate_session(
            object(),  # type: ignore[arg-type]
            SQLiteDescriptor(),
        )
    with pytest.raises(StorageException):
        validator.validate_result(object())  # type: ignore[arg-type]
    with pytest.raises(StorageException):
        SQLiteStorageFactory(tmp_path / "bad.sqlite3", timeout=False)
    with pytest.raises(StorageException):
        SQLiteStorage(tmp_path / "bad-storage.sqlite3", timeout=0)


def test_additional_storage_validation_paths(
    storage: SQLiteStorage,
) -> None:
    assert storage.resolver.database == storage.database
    with pytest.raises(StorageException):
        storage.transaction(object())
    wrong_type = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            parameters={"sqlite_operation": 7},
        )
    )
    assert not wrong_type.success
    invalid_base64 = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            parameters={"content_base64": "not base64"},
        )
    )
    assert not invalid_base64.success
    conflicting = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            parameters={"content_base64": "YQ==", "content": "a"},
        )
    )
    assert not conflicting.success
    missing_target = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            parameters={"sqlite_operation": "copy"},
        )
    )
    assert not missing_target.success
