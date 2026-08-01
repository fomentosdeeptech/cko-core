"""Complete tests for the SPR-008T Filesystem Storage Connector."""

from __future__ import annotations

import base64
import json
import logging
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

from cko.core.connectors import (
    Connector,
    ConnectorContext,
    ConnectorResult,
    ConnectorSession,
)
from cko.core.storage import (
    Storage,
    StorageContext,
    StorageException,
    StorageLocation,
    StorageOperation,
    StorageResult,
    StorageSession,
)
from cko.core.storage.filesystem import (
    FILESYSTEM_IDENTIFIER,
    FILESYSTEM_OPERATIONS,
    FILESYSTEM_SCHEMA_VERSION,
    FILESYSTEM_VERSION,
    FilesystemConnector,
    FilesystemDescriptor,
    FilesystemLocationResolver,
    FilesystemResult,
    FilesystemSession,
    FilesystemStorage,
    FilesystemStorageFactory,
    FilesystemStorageValidator,
)


NOW = datetime(2026, 7, 21, 12, 0, tzinfo=timezone.utc)


def location(key: str, namespace: str = "knowledge") -> StorageLocation:
    return StorageLocation(namespace=namespace, key=key)


def storage_session(
    operation: StorageOperation,
    logical_location: StorageLocation,
    parameters: dict[str, object] | None = None,
    session_id: str = "storage-session",
) -> StorageSession:
    context = StorageContext(
        correlation_id="correlation-001",
        operation=operation,
        location=logical_location,
        parameters={} if parameters is None else parameters,
    )
    return StorageSession.start(
        session_id,
        FILESYSTEM_IDENTIFIER,
        context,
        NOW,
    )


def connector_session(
    operation: str,
    logical_location: StorageLocation,
    parameters: dict[str, object] | None = None,
    session_id: str = "connector-session",
) -> ConnectorSession:
    values = {"location": logical_location.to_dict()}
    values.update({} if parameters is None else parameters)
    context = ConnectorContext(
        correlation_id="correlation-001",
        operation=operation,
        parameters=values,
    )
    return ConnectorSession.start(
        session_id,
        FILESYSTEM_IDENTIFIER,
        context,
        NOW,
    )


@pytest.fixture
def storage(tmp_path: Path) -> FilesystemStorage:
    return FilesystemStorage(tmp_path / "root")


def test_public_api_versions_and_contract_implementations(tmp_path: Path) -> None:
    descriptor = FilesystemDescriptor()
    storage = FilesystemStorage(tmp_path / "storage")
    connector = FilesystemConnector(tmp_path / "connector")
    assert isinstance(storage, Storage)
    assert isinstance(connector, Connector)
    assert descriptor.storage.identifier == FILESYSTEM_IDENTIFIER
    assert descriptor.connector.identifier == FILESYSTEM_IDENTIFIER
    assert FILESYSTEM_VERSION == "1.0.0"
    assert FILESYSTEM_SCHEMA_VERSION == "1.0"
    assert FILESYSTEM_OPERATIONS == tuple(sorted(FILESYSTEM_OPERATIONS))


def test_descriptor_is_frozen_and_serializable() -> None:
    descriptor = FilesystemDescriptor()
    encoded = descriptor.to_json()
    assert encoded == json.dumps(
        descriptor.to_dict(),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert FilesystemDescriptor.from_json(encoded) == descriptor
    with pytest.raises(FrozenInstanceError):
        descriptor.schema_version = "2.0"  # type: ignore[misc]


def test_location_resolver_round_trip_and_confinement(tmp_path: Path) -> None:
    resolver = FilesystemLocationResolver(tmp_path)
    logical = location("folder/file.txt")
    physical = resolver.resolve(logical)
    assert physical == (tmp_path / "knowledge/folder/file.txt").resolve()
    assert resolver.logical(physical) == logical
    assert resolver.logical(tmp_path / "knowledge") == location(".")
    with pytest.raises(StorageException, match="relative logical path"):
        resolver.resolve(location("../outside.txt"))
    with pytest.raises(StorageException, match="outside"):
        resolver.logical(tmp_path.parent / "outside.txt")


def test_create_file_and_directory(storage: FilesystemStorage) -> None:
    file_result = storage.create(
        storage_session(
            StorageOperation.WRITE,
            location("created.txt"),
            {"content": "criação", "encoding": "utf-8"},
        )
    )
    directory_result = storage.create(
        storage_session(
            StorageOperation.WRITE,
            location("folder"),
            {"kind": "directory"},
            "directory-session",
        )
    )
    assert file_result.success
    assert directory_result.success
    assert (storage.resolver.root / "knowledge/created.txt").read_text(
        encoding="utf-8"
    ) == "criação"
    assert (storage.resolver.root / "knowledge/folder").is_dir()


def test_write_and_read_text(storage: FilesystemStorage) -> None:
    logical = location("text.txt")
    written = storage.execute(
        storage_session(
            StorageOperation.WRITE,
            logical,
            {"content": "conteúdo", "encoding": "utf-8"},
        )
    )
    read = storage.execute(
        storage_session(
            StorageOperation.READ,
            logical,
            {"include_text": True},
            "read-session",
        )
    )
    assert written.success
    assert read.success
    assert read.metadata["content"] == "conteúdo"
    assert base64.b64decode(read.metadata["content_base64"]) == (
        "conteúdo".encode()
    )


def test_write_and_read_binary_base64(storage: FilesystemStorage) -> None:
    content = bytes(range(32))
    encoded = base64.b64encode(content).decode("ascii")
    logical = location("binary.bin")
    assert storage.write(
        storage_session(
            StorageOperation.WRITE,
            logical,
            {"content_base64": encoded},
        )
    ).success
    result = storage.read(
        storage_session(
            StorageOperation.READ,
            logical,
            session_id="binary-read",
        )
    )
    assert result.metadata["content_base64"] == encoded
    assert result.objects[0].digest is not None
    assert result.objects[0].digest.startswith("sha256:")


def test_exists_and_metadata(storage: FilesystemStorage) -> None:
    logical = location("metadata.txt")
    storage.write(
        storage_session(
            StorageOperation.WRITE,
            logical,
            {"content": "1234"},
        )
    )
    exists = storage.exists(
        storage_session(StorageOperation.EXISTS, logical, session_id="exists")
    )
    metadata = storage.metadata(
        storage_session(
            StorageOperation.METADATA,
            logical,
            session_id="metadata",
        )
    )
    missing = storage.exists(
        storage_session(
            StorageOperation.EXISTS,
            location("missing"),
            session_id="missing",
        )
    )
    assert exists.metadata["exists"] is True
    assert metadata.objects[0].size == 4
    assert metadata.objects[0].metadata["is_directory"] is False
    assert missing.metadata["exists"] is False
    assert missing.objects == ()


def test_list_is_deterministic_and_recursive(storage: FilesystemStorage) -> None:
    for key in ("folder/z.txt", "folder/a.txt", "folder/sub/b.txt"):
        storage.write(
            storage_session(
                StorageOperation.WRITE,
                location(key),
                {"content": key},
                key,
            )
        )
    direct = storage.list(
        storage_session(
            StorageOperation.LIST,
            location("folder"),
            session_id="direct-list",
        )
    )
    recursive = storage.list(
        storage_session(
            StorageOperation.LIST,
            location("folder"),
            {"recursive": True},
            "recursive-list",
        )
    )
    assert [item.location.key for item in direct.objects] == [
        "folder/a.txt",
        "folder/sub",
        "folder/z.txt",
    ]
    recursive_keys = [item.location.key for item in recursive.objects]
    assert recursive_keys == sorted(recursive_keys)
    assert "folder/sub/b.txt" in recursive_keys


def test_copy_and_move(storage: FilesystemStorage) -> None:
    source = location("source.txt")
    copied = location("copied.txt")
    moved = location("moved.txt")
    storage.write(
        storage_session(
            StorageOperation.WRITE,
            source,
            {"content": "payload"},
        )
    )
    copy_result = storage.copy(
        storage_session(
            StorageOperation.WRITE,
            source,
            {"target": copied.to_dict()},
            "copy-session",
        )
    )
    move_result = storage.move(
        storage_session(
            StorageOperation.WRITE,
            copied,
            {"target": moved.to_dict()},
            "move-session",
        )
    )
    assert copy_result.success
    assert move_result.success
    assert storage.resolver.resolve(source).exists()
    assert not storage.resolver.resolve(copied).exists()
    assert storage.resolver.resolve(moved).read_text() == "payload"


def test_delete_file_and_recursive_directory(storage: FilesystemStorage) -> None:
    nested = location("tree/item.txt")
    storage.write(
        storage_session(
            StorageOperation.WRITE,
            nested,
            {"content": "payload"},
        )
    )
    deleted = storage.delete(
        storage_session(
            StorageOperation.DELETE,
            nested,
            session_id="delete-file",
        )
    )
    assert deleted.success
    storage.write(
        storage_session(
            StorageOperation.WRITE,
            nested,
            {"content": "payload"},
            "rewrite",
        )
    )
    tree = storage.delete(
        storage_session(
            StorageOperation.DELETE,
            location("tree"),
            {"recursive": True},
            "delete-tree",
        )
    )
    assert tree.success
    assert not storage.resolver.resolve(location("tree")).exists()


@pytest.mark.parametrize(
    ("parameters", "message"),
    [
        ({"content_base64": "not base64"}, "invalid"),
        ({"content": "x", "content_base64": "eA=="}, "exclusive"),
        ({"content": 42}, "string"),
    ],
)
def test_write_error_results(
    storage: FilesystemStorage,
    parameters: dict[str, object],
    message: str,
) -> None:
    result = storage.write(
        storage_session(StorageOperation.WRITE, location("bad"), parameters)
    )
    assert not result.success
    assert message in (result.message or "")


def test_missing_and_invalid_operations_return_failures(
    storage: FilesystemStorage,
) -> None:
    missing = storage.read(
        storage_session(StorageOperation.READ, location("missing"))
    )
    incompatible = storage.execute(
        storage_session(
            StorageOperation.READ,
            location("missing"),
            {"filesystem_operation": "write"},
            "incompatible",
        )
    )
    assert not missing.success
    assert not incompatible.success
    assert "incompatible" in (incompatible.message or "")


def test_connector_executes_all_adapter_operations(tmp_path: Path) -> None:
    connector = FilesystemConnector(tmp_path)
    source = location("connector/source.txt")
    copied = location("connector/copied.txt")
    moved = location("connector/moved.txt")
    operations = [
        connector_session("create", source, {"content": "connector"}, "1"),
        connector_session("read", source, session_id="2"),
        connector_session(
            "copy", source, {"target": copied.to_dict()}, "3"
        ),
        connector_session(
            "move", copied, {"target": moved.to_dict()}, "4"
        ),
        connector_session("exists", moved, session_id="5"),
        connector_session("metadata", moved, session_id="6"),
        connector_session(
            "list", location("connector"), session_id="7"
        ),
        connector_session(
            "write", moved, {"content": "updated"}, "8"
        ),
        connector_session("delete", moved, session_id="9"),
    ]
    results = [connector.execute(item) for item in operations]
    assert all(isinstance(item, ConnectorResult) for item in results)
    assert all(item.success for item in results)
    storage_results = []
    for item in results:
        serialized = item.to_dict()["data"]
        assert isinstance(serialized, dict)
        nested = serialized["storage_result"]
        assert isinstance(nested, dict)
        storage_results.append(StorageResult.from_dict(nested))
    assert all(item.storage_id == FILESYSTEM_IDENTIFIER for item in storage_results)


def test_connector_rejects_invalid_operation_and_location(tmp_path: Path) -> None:
    connector = FilesystemConnector(tmp_path)
    unsupported = connector.execute(
        connector_session("unsupported", location("item"))
    )
    context = ConnectorContext(
        correlation_id="correlation",
        operation="read",
        parameters={},
    )
    missing_location = connector.execute(
        ConnectorSession.start(
            "missing-location",
            FILESYSTEM_IDENTIFIER,
            context,
            NOW,
        )
    )
    assert not unsupported.success
    assert not missing_location.success


def test_session_and_result_bridges_round_trip(tmp_path: Path) -> None:
    connector = FilesystemConnector(tmp_path)
    public_session = connector_session(
        "write", location("bridge.txt"), {"content": "bridge"}
    )
    bridge = FilesystemSession.from_connector(public_session)
    storage_result = connector.storage.execute(bridge.storage_session)
    result = FilesystemResult.from_storage(bridge, storage_result)
    assert FilesystemSession.from_json(bridge.to_json()) == bridge
    assert FilesystemResult.from_json(result.to_json()) == result
    assert result.connector_result.success


def test_factory_integrates_generic_connector_and_storage_factories(
    tmp_path: Path,
) -> None:
    factory = FilesystemStorageFactory(tmp_path)
    storage = factory.create_storage()
    connector = factory.create_connector()
    assert isinstance(storage, FilesystemStorage)
    assert isinstance(connector, FilesystemConnector)
    assert storage.descriptor == factory.descriptor.storage
    assert connector.descriptor == factory.descriptor.connector


def test_validator_checks_descriptor_session_result_and_root(
    tmp_path: Path,
) -> None:
    validator = FilesystemStorageValidator()
    descriptor = validator.validate_descriptor(FilesystemDescriptor())
    bridge = FilesystemSession.from_connector(
        connector_session("exists", location("item"))
    )
    validator.validate_session(bridge, descriptor)
    storage_result = StorageResult(
        storage_id=FILESYSTEM_IDENTIFIER,
        operation=StorageOperation.EXISTS,
        success=True,
        metadata={"exists": False},
    )
    result = FilesystemResult.from_storage(bridge, storage_result)
    assert validator.validate_result(result) is result
    assert validator.validate_root(tmp_path).root == tmp_path.resolve()
    with pytest.raises(StorageException, match="FilesystemDescriptor"):
        validator.validate_descriptor(object())  # type: ignore[arg-type]


def test_required_structured_logging_events(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    connector = FilesystemConnector(tmp_path)
    source = location("log/source.txt")
    copied = location("log/copied.txt")
    moved = location("log/moved.txt")
    sessions = [
        connector_session("write", source, {"content": "x"}, "log-1"),
        connector_session("read", source, session_id="log-2"),
        connector_session(
            "copy", source, {"target": copied.to_dict()}, "log-3"
        ),
        connector_session(
            "move", copied, {"target": moved.to_dict()}, "log-4"
        ),
        connector_session(
            "list", location("log"), session_id="log-5"
        ),
        connector_session("delete", moved, session_id="log-6"),
    ]
    assert all(connector.execute(item).success for item in sessions)
    events = {getattr(record, "event", None) for record in caplog.records}
    assert {
        "filesystem_open",
        "filesystem_read",
        "filesystem_write",
        "filesystem_delete",
        "filesystem_copy",
        "filesystem_move",
        "filesystem_list",
    }.issubset(events)


def test_package_has_no_runtime_dependency() -> None:
    package = Path("src/cko/core/storage/filesystem")
    for source in package.glob("*.py"):
        text = source.read_text(encoding="utf-8")
        assert "cko.core.runtime" not in text
        assert "import Runtime" not in text


@pytest.mark.parametrize(
    ("model_type", "message"),
    [
        (FilesystemDescriptor, "descriptor"),
        (FilesystemSession, "session"),
        (FilesystemResult, "result"),
    ],
)
def test_filesystem_models_reject_invalid_envelopes_and_json(
    model_type: type,
    message: str,
) -> None:
    with pytest.raises(StorageException, match=message):
        model_type.from_dict({})
    with pytest.raises(StorageException, match=message):
        model_type.from_json("{")
    with pytest.raises(StorageException, match=message):
        model_type.from_json("[]")


def test_filesystem_models_reject_invalid_composition() -> None:
    descriptor = FilesystemDescriptor()
    with pytest.raises(StorageException, match="StorageDescriptor"):
        FilesystemDescriptor(
            storage_descriptor=object(),  # type: ignore[arg-type]
        )
    different_connector = descriptor.connector.to_dict()
    different_connector["identifier"] = "different"
    with pytest.raises(StorageException, match="identifiers"):
        FilesystemDescriptor(
            connector_descriptor=type(descriptor.connector).from_dict(
                different_connector
            )
        )
    session = FilesystemSession.from_connector(
        connector_session("read", location("item"))
    )
    with pytest.raises(StorageException, match="identifiers"):
        FilesystemSession(
            session.connector_session,
            storage_session(
                StorageOperation.READ,
                location("item"),
                session_id="different",
            ),
        )
    successful = StorageResult(
        storage_id=FILESYSTEM_IDENTIFIER,
        operation=StorageOperation.READ,
        success=True,
    )
    bridge_result = FilesystemResult.from_storage(session, successful)
    failed = StorageResult(
        storage_id=FILESYSTEM_IDENTIFIER,
        operation=StorageOperation.READ,
        success=False,
        message="failure",
    )
    with pytest.raises(StorageException, match="success"):
        FilesystemResult(bridge_result.connector_result, failed)


def test_resolver_rejects_invalid_values(tmp_path: Path) -> None:
    with pytest.raises(StorageException, match="root"):
        FilesystemLocationResolver(" ")
    resolver = FilesystemLocationResolver(tmp_path)
    with pytest.raises(StorageException, match="StorageLocation"):
        resolver.resolve(object())  # type: ignore[arg-type]
    with pytest.raises(StorageException, match="path"):
        resolver.logical(" ")
    with pytest.raises(StorageException, match="namespace"):
        resolver.logical(tmp_path)


def test_directory_copy_and_nonrecursive_delete(
    storage: FilesystemStorage,
) -> None:
    source = location("source-directory")
    target = location("target-directory")
    assert storage.create(
        storage_session(
            StorageOperation.WRITE,
            source,
            {"kind": "directory"},
        )
    ).success
    copied = storage.copy(
        storage_session(
            StorageOperation.WRITE,
            source,
            {"target": target.to_dict()},
            "copy-directory",
        )
    )
    deleted = storage.delete(
        storage_session(
            StorageOperation.DELETE,
            target,
            session_id="delete-directory",
        )
    )
    assert copied.success
    assert deleted.success


def test_additional_operation_errors(storage: FilesystemStorage) -> None:
    invalid_kind = storage.create(
        storage_session(
            StorageOperation.WRITE,
            location("kind"),
            {"kind": "invalid"},
        )
    )
    invalid_list = storage.list(
        storage_session(
            StorageOperation.LIST,
            location("missing-directory"),
            session_id="bad-list",
        )
    )
    missing_target = storage.copy(
        storage_session(
            StorageOperation.WRITE,
            location("source"),
            session_id="bad-copy",
        )
    )
    assert not invalid_kind.success
    assert not invalid_list.success
    assert not missing_target.success


def test_validator_and_factory_reject_invalid_composition(tmp_path: Path) -> None:
    with pytest.raises(StorageException, match="storage_validator"):
        FilesystemStorageValidator(
            storage_validator=object(),  # type: ignore[arg-type]
        )
    validator = FilesystemStorageValidator()
    with pytest.raises(StorageException, match="FilesystemSession"):
        validator.validate_session(
            object(),  # type: ignore[arg-type]
            FilesystemDescriptor(),
        )
    with pytest.raises(StorageException, match="FilesystemResult"):
        validator.validate_result(object())  # type: ignore[arg-type]
    with pytest.raises(StorageException, match="validator"):
        FilesystemStorageFactory(
            tmp_path,
            validator=object(),  # type: ignore[arg-type]
        )
