"""Acceptance tests for SPR-008V checkpoint and snapshot foundation."""

from __future__ import annotations

import ast
import json
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import MappingProxyType

import pytest

from cko.core import (
    CHECKPOINT_SCHEMA_VERSION,
    CHECKPOINT_VERSION,
    CheckpointCollection,
    CheckpointConflictError,
    CheckpointContext,
    CheckpointEngine,
    CheckpointException,
    CheckpointIdentifier,
    CheckpointIntegrityError,
    CheckpointMetadata,
    CheckpointNotFoundError,
    CheckpointOperation,
    CheckpointPayload,
    CheckpointQuery,
    CheckpointRecord,
    CheckpointRepository,
    CheckpointResult,
    CheckpointSerializationError,
    CheckpointSerializer,
    CheckpointSnapshot,
    CheckpointState,
    CheckpointStateError,
    CheckpointStorageError,
    CheckpointValidationError,
    CheckpointValidator,
    DefaultCheckpointEngine,
    DefaultCheckpointSerializer,
    StorageCheckpointRepository,
    Storage,
    StorageCapabilities,
    StorageDescriptor,
    StorageException,
    StorageMetadata,
    StorageOperation,
    StorageResult,
)
from cko.core.storage.filesystem import FilesystemStorage
from cko.core.storage.sqlite import SQLiteStorage


UTC = timezone.utc
INSTANT = datetime(2026, 7, 23, 12, 0, tzinfo=UTC)


def metadata() -> CheckpointMetadata:
    """Build canonical metadata for tests."""
    return CheckpointMetadata(
        name="inventory",
        description="Inventory execution checkpoint",
        producer="cko-core-tests",
        producer_version="1.0.0",
        labels={"environment": "test", "nested": {"safe": True}},
        attributes={"attempt": 1, "modes": ["full", "verified"]},
    )


def context(
    operation: CheckpointOperation = CheckpointOperation.CREATE,
) -> CheckpointContext:
    """Build a safe canonical context."""
    return CheckpointContext(
        correlation_id="correlation-001",
        operation=operation,
        namespace="inventory",
        subject_id="subject-001",
        parameters={"requested_by": "suite"},
        metadata={"tenant": "test"},
    )


def record(
    *,
    checkpoint_id: str = "checkpoint-001",
    sequence: int = 0,
    state: CheckpointState = CheckpointState.CREATED,
    parent_checkpoint_id: str | None = None,
    instant: datetime = INSTANT,
) -> CheckpointRecord:
    """Build a valid record."""
    identifier = CheckpointIdentifier(
        checkpoint_id=checkpoint_id,
        namespace="inventory",
        subject_id="subject-001",
        sequence=sequence,
        created_at=instant,
    )
    return CheckpointRecord(
        identifier=identifier,
        metadata=metadata(),
        payload=CheckpointPayload(
            content_type="application/json",
            encoding="utf-8",
            data={
                "items": [1, 2, {"raw": b"\x00\xff"}],
                "enabled": True,
                "optional": None,
            },
        ),
        state=state,
        correlation_id="correlation-001",
        parent_checkpoint_id=parent_checkpoint_id,
        created_at=instant,
        updated_at=instant,
    )


@pytest.fixture(params=("filesystem", "sqlite"))
def storage(request: pytest.FixtureRequest, tmp_path: Path):
    """Provide each homologated Storage adapter with safe cleanup."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    if request.param == "filesystem":
        instance = FilesystemStorage(tmp_path / "objects")
    else:
        instance = SQLiteStorage(tmp_path / "checkpoints.db")
    try:
        yield instance
    finally:
        close = getattr(instance, "close", None)
        if close is not None:
            close()


def engine_for(storage) -> DefaultCheckpointEngine:
    """Create a fully injected engine for one Storage provider."""
    serializer = DefaultCheckpointSerializer()
    validator = CheckpointValidator()
    repository = StorageCheckpointRepository(
        storage,
        serializer,
        validator,
        clock=lambda: INSTANT,
        session_id_factory=lambda: "storage-session-001",
    )
    identifiers = iter(
        (
            "checkpoint-001",
            "snapshot-create",
            "snapshot-store",
            "snapshot-restore",
            "checkpoint-002",
            "snapshot-create-2",
            "snapshot-store-2",
            "snapshot-supersede",
        )
    )
    return DefaultCheckpointEngine(
        repository,
        serializer,
        validator,
        clock=lambda: INSTANT,
        id_factory=lambda: next(identifiers),
    )


def test_public_constants_contracts_and_enums() -> None:
    assert CHECKPOINT_SCHEMA_VERSION == "1.0"
    assert CHECKPOINT_VERSION == "1.0.0"
    assert issubclass(DefaultCheckpointEngine, CheckpointEngine)
    assert issubclass(StorageCheckpointRepository, CheckpointRepository)
    assert issubclass(DefaultCheckpointSerializer, CheckpointSerializer)
    assert {item.value for item in CheckpointState} == {
        "created", "stored", "restored", "superseded", "failed",
    }
    assert {item.value for item in CheckpointOperation} == {
        "create", "store", "restore", "list", "inspect", "supersede",
        "delete",
    }


def test_models_are_frozen_slotted_deeply_immutable_and_safe() -> None:
    item = record()
    with pytest.raises(FrozenInstanceError):
        item.state = CheckpointState.STORED
    assert not hasattr(item, "__dict__")
    assert isinstance(item.metadata.labels, MappingProxyType)
    assert isinstance(item.metadata.labels["nested"], MappingProxyType)
    assert item.metadata.attributes["modes"] == ("full", "verified")
    with pytest.raises(TypeError):
        item.metadata.labels["new"] = "value"
    assert "raw" not in repr(item)


def test_identifier_normalizes_aware_timestamp_to_utc() -> None:
    local = timezone(timedelta(hours=-3))
    identifier = CheckpointIdentifier(
        "id", "namespace", "subject", 0,
        datetime(2026, 7, 23, 9, 0, tzinfo=local),
    )
    assert identifier.created_at == INSTANT
    assert identifier.created_at.tzinfo is UTC
    with pytest.raises(CheckpointValidationError):
        CheckpointIdentifier("id", "namespace", "subject", 0, INSTANT.replace(
            tzinfo=None
        ))
    with pytest.raises(CheckpointValidationError):
        CheckpointIdentifier("", "namespace", "subject", 0, INSTANT)
    with pytest.raises(CheckpointValidationError):
        CheckpointIdentifier("id", "namespace", "subject", -1, INSTANT)


def test_payload_canonical_size_digest_bytes_and_integrity() -> None:
    first = CheckpointPayload(
        "application/json",
        "utf-8",
        {"z": [1, b"\x01"], "a": "ação"},
    )
    second = CheckpointPayload(
        "application/json",
        "UTF-8",
        {"a": "ação", "z": (1, b"\x01")},
    )
    assert first == second
    assert first.size == len(
        '{"a":"ação","z":[1,{"$binary":"AQ==","$encoding":"base64"}]}'.encode(
            "utf-8"
        )
    )
    assert len(first.sha256) == 64
    assert CheckpointPayload.from_json(first.to_json()) == first
    envelope = first.to_dict()
    envelope["sha256"] = "0" * 64
    with pytest.raises(CheckpointIntegrityError):
        CheckpointPayload.from_dict(envelope)
    with pytest.raises(CheckpointValidationError):
        CheckpointPayload("application/json", "utf-8", float("nan"))


def test_all_models_support_strict_deterministic_round_trip() -> None:
    item = record()
    snapshot = CheckpointSnapshot.capture("snapshot-001", item, INSTANT)
    query = CheckpointQuery(
        namespace="inventory",
        subject_id="subject-001",
        checkpoint_id="checkpoint-001",
        state=CheckpointState.CREATED,
        sequence_min=0,
        sequence_max=2,
        created_from=INSTANT,
        created_to=INSTANT,
        limit=5,
        descending=True,
    )
    collection = CheckpointCollection((item,), total=1)
    result = CheckpointResult(
        success=True,
        operation=CheckpointOperation.INSPECT,
        checkpoint=item,
        snapshot=snapshot,
        collection=collection,
        metadata={"verified": True},
    )
    models = (
        item.identifier,
        item.metadata,
        item.payload,
        item,
        snapshot,
        context(),
        query,
        collection,
        result,
    )
    for model in models:
        rebuilt = type(model).from_json(model.to_json())
        assert rebuilt == model
        assert rebuilt.model == model.model
        assert model.to_json() == rebuilt.to_json()
        assert ": " not in model.to_json()
        assert ", " not in model.to_json()


def test_strict_deserialization_rejects_extra_version_and_model() -> None:
    payload = record().to_dict()
    for key, value in (
        ("extra", True),
        ("schema_version", "2.0"),
        ("model", "unknown"),
    ):
        changed = dict(payload)
        changed[key] = value
        with pytest.raises(CheckpointSerializationError):
            CheckpointRecord.from_dict(changed)


def test_record_snapshot_query_collection_and_result_invariants() -> None:
    item = record()
    with pytest.raises(CheckpointValidationError):
        CheckpointRecord(
            identifier=item.identifier,
            metadata=item.metadata,
            payload=item.payload,
            state=item.state,
            correlation_id=item.correlation_id,
            parent_checkpoint_id=None,
            created_at=item.created_at,
            updated_at=item.created_at - timedelta(seconds=1),
        )
    with pytest.raises(CheckpointIntegrityError):
        CheckpointSnapshot(
            "snapshot", item, INSTANT, "0" * 64, item.identifier.sequence
        )
    with pytest.raises(CheckpointValidationError):
        CheckpointQuery(sequence_min=2, sequence_max=1)
    with pytest.raises(CheckpointValidationError):
        CheckpointQuery(limit=0)
    with pytest.raises(CheckpointValidationError):
        CheckpointResult(
            success=True,
            operation=CheckpointOperation.LIST,
            error_code="bad",
            error_message="bad",
        )
    with pytest.raises(CheckpointValidationError):
        CheckpointResult(
            success=False,
            operation=CheckpointOperation.LIST,
        )


def test_serializer_is_canonical_strict_and_detects_corruption() -> None:
    serializer = DefaultCheckpointSerializer()
    item = record()
    payload = serializer.serialize(item)
    assert payload == item.to_json().encode("utf-8")
    assert serializer.deserialize(payload) == item
    assert len(serializer.digest(item)) == 64
    noncanonical = json.dumps(
        item.to_dict(), ensure_ascii=True, indent=2
    ).encode("utf-8")
    with pytest.raises(CheckpointSerializationError):
        serializer.deserialize(noncanonical)
    corrupted = bytearray(payload)
    corrupted[-2] = ord("x")
    with pytest.raises(CheckpointSerializationError):
        serializer.deserialize(bytes(corrupted))
    with pytest.raises(CheckpointSerializationError):
        serializer.deserialize(b"\xff")


def test_validator_transitions_context_and_physical_reference_rejection() -> None:
    validator = CheckpointValidator()
    validator.validate_transition(
        CheckpointState.CREATED, CheckpointState.STORED
    )
    validator.validate_transition(
        CheckpointState.STORED, CheckpointState.RESTORED
    )
    validator.validate_transition(
        CheckpointState.STORED, CheckpointState.SUPERSEDED
    )
    with pytest.raises(CheckpointStateError):
        validator.validate_transition(
            CheckpointState.SUPERSEDED, CheckpointState.STORED
        )
    with pytest.raises(CheckpointStateError):
        validator.validate_transition(
            CheckpointState.FAILED, CheckpointState.CREATED
        )
    with pytest.raises(CheckpointValidationError):
        validator.validate_context(
            context(CheckpointOperation.CREATE),
            CheckpointOperation.STORE,
        )
    unsafe = CheckpointContext(
        "correlation",
        CheckpointOperation.CREATE,
        "namespace",
        "subject",
        parameters={"path": "forbidden"},
    )
    with pytest.raises(CheckpointValidationError):
        validator.validate_context(unsafe)
    with pytest.raises(CheckpointValidationError):
        validator.validate_identifier(
            CheckpointIdentifier(
                "../id", "namespace", "subject", 0, INSTANT
            )
        )


def test_exception_hierarchy_and_safe_representation() -> None:
    errors = (
        CheckpointValidationError("validation"),
        CheckpointSerializationError("serialization"),
        CheckpointIntegrityError("integrity"),
        CheckpointNotFoundError("missing"),
        CheckpointConflictError("conflict"),
        CheckpointStorageError("storage"),
        CheckpointStateError("state"),
    )
    assert all(isinstance(error, CheckpointException) for error in errors)
    assert all(error.to_dict()["code"] for error in errors)


def test_engine_create_does_not_persist_and_store_is_explicit(storage) -> None:
    engine = engine_for(storage)
    created = engine.create(context(), metadata(), {"value": 1})
    assert created.success
    assert created.checkpoint is not None
    assert created.checkpoint.state is CheckpointState.CREATED
    assert created.snapshot is not None
    empty = engine.list(CheckpointQuery())
    assert empty.success and len(empty.collection) == 0
    stored = engine.store(created.checkpoint)
    assert stored.success
    assert stored.checkpoint.state is CheckpointState.STORED
    assert len(engine.list(CheckpointQuery()).collection) == 1


def test_filesystem_and_sqlite_full_lifecycle(storage) -> None:
    engine = engine_for(storage)
    created = engine.create(context(), metadata(), {"value": b"payload"})
    stored = engine.store(created.checkpoint)
    restored = engine.restore(stored.checkpoint.identifier)
    assert restored.success
    assert restored.checkpoint.state is CheckpointState.RESTORED
    assert restored.checkpoint.payload.data["value"] == b"payload"
    inspected = engine.inspect(stored.checkpoint.identifier)
    assert inspected.success
    assert inspected.checkpoint.state is CheckpointState.STORED
    deleted = engine.delete(stored.checkpoint.identifier)
    assert deleted.success
    missing = engine.restore(stored.checkpoint.identifier)
    assert not missing.success
    assert missing.error_code == "checkpoint_not_found"


def test_listing_filters_order_limit_and_total(storage) -> None:
    repository = StorageCheckpointRepository(storage)
    for sequence, state in (
        (2, CheckpointState.STORED),
        (0, CheckpointState.STORED),
        (1, CheckpointState.SUPERSEDED),
    ):
        result = repository.store(
            record(
                checkpoint_id=f"checkpoint-{sequence}",
                sequence=sequence,
                state=state,
                instant=INSTANT + timedelta(minutes=sequence),
            )
        )
        assert result.success
    ascending = repository.list(
        CheckpointQuery(
            namespace="inventory",
            subject_id="subject-001",
            sequence_min=0,
            sequence_max=2,
            created_from=INSTANT,
            created_to=INSTANT + timedelta(minutes=2),
        )
    )
    assert [
        item.identifier.sequence
        for item in ascending.collection.checkpoints
    ] == [0, 1, 2]
    limited = repository.list(
        CheckpointQuery(
            state=CheckpointState.STORED,
            descending=True,
            limit=1,
        )
    )
    assert limited.collection.total == 2
    assert len(limited.collection) == 1
    assert limited.collection.checkpoints[0].identifier.sequence == 2
    by_id = repository.list(
        CheckpointQuery(checkpoint_id="checkpoint-1")
    )
    assert len(by_id.collection) == 1


def test_store_conflict_and_missing_operations_are_typed(storage) -> None:
    repository = StorageCheckpointRepository(storage)
    item = record(state=CheckpointState.STORED)
    assert repository.store(item).success
    conflict = repository.store(item)
    assert not conflict.success
    assert conflict.error_code == "checkpoint_conflict"
    missing_id = CheckpointIdentifier(
        "missing", "inventory", "subject-001", 99, INSTANT
    )
    for result in (
        repository.restore(missing_id),
        repository.inspect(missing_id),
        repository.delete(missing_id),
    ):
        assert not result.success
        assert result.error_code == "checkpoint_not_found"


def test_supersede_requires_and_preserves_successor_traceability(storage) -> None:
    engine = engine_for(storage)
    first = engine.create(context(), metadata(), {"generation": 1})
    stored_first = engine.store(first.checkpoint)
    second = engine.create(
        context(),
        metadata(),
        {"generation": 2},
        sequence=1,
        parent_checkpoint_id=stored_first.checkpoint.identifier.checkpoint_id,
    )
    stored_second = engine.store(second.checkpoint)
    superseded = engine.supersede(
        stored_first.checkpoint, stored_second.checkpoint
    )
    assert superseded.success
    assert superseded.checkpoint.state is CheckpointState.SUPERSEDED
    persisted = engine.inspect(stored_first.checkpoint.identifier)
    assert persisted.checkpoint.state is CheckpointState.SUPERSEDED
    assert (
        superseded.metadata["successor_checkpoint_id"]
        == stored_second.checkpoint.identifier.checkpoint_id
    )


def test_structured_logging_contains_events_without_payload(storage, caplog) -> None:
    caplog.set_level("INFO", logger="cko.core.checkpoint")
    engine = engine_for(storage)
    created = engine.create(
        context(), metadata(), {"secret_content": "must-not-be-logged"}
    )
    stored = engine.store(created.checkpoint)
    engine.restore(stored.checkpoint.identifier)
    engine.list(CheckpointQuery())
    engine.inspect(stored.checkpoint.identifier)
    engine.delete(stored.checkpoint.identifier)
    events = {getattr(item, "event", None) for item in caplog.records}
    assert {
        "checkpoint_created",
        "checkpoint_validated",
        "checkpoint_serialized",
        "checkpoint_stored",
        "checkpoint_restored",
        "checkpoint_listed",
        "checkpoint_inspected",
        "checkpoint_deleted",
    } <= events
    assert "must-not-be-logged" not in caplog.text


def test_repository_has_no_adapter_runtime_path_or_database_imports() -> None:
    repository_path = (
        Path(__file__).parents[1]
        / "src" / "cko" / "core" / "checkpoint" / "repository.py"
    )
    source = repository_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert "cko.core.storage.filesystem" not in imports
    assert "cko.core.storage.sqlite" not in imports
    assert "sqlite3" not in imports
    assert "pathlib" not in imports
    assert not any("runtime" in name for name in imports)


def test_package_files_are_utf8_valid_ast_and_have_no_placeholders() -> None:
    package = (
        Path(__file__).parents[1] / "src" / "cko" / "core" / "checkpoint"
    )
    for path in package.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        ast.parse(source)
        assert "TODO" not in source
        assert "\ufffd" not in source


def test_additional_model_validation_and_decode_failures() -> None:
    item = record()
    invalid_calls = (
        lambda: CheckpointIdentifier(
            "id", "namespace", "subject", 0, INSTANT,
            schema_version="2.0",
        ),
        lambda: CheckpointMetadata(
            "n", "d", "p", "1", schema_version="2.0"
        ),
        lambda: CheckpointPayload("json", "latin-1", {}),
        lambda: CheckpointPayload("json", "utf-8", {}, size=99),
        lambda: CheckpointPayload(
            "json", "utf-8", {}, schema_version="2.0"
        ),
        lambda: CheckpointPayload("json", "utf-8", object()),
        lambda: CheckpointRecord(
            "bad", item.metadata, item.payload, item.state, "c", None,
            item.created_at, item.updated_at,
        ),
        lambda: CheckpointRecord(
            item.identifier, "bad", item.payload, item.state, "c", None,
            item.created_at, item.updated_at,
        ),
        lambda: CheckpointRecord(
            item.identifier, item.metadata, "bad", item.state, "c", None,
            item.created_at, item.updated_at,
        ),
        lambda: CheckpointRecord(
            item.identifier, item.metadata, item.payload, "bad", "c", None,
            item.created_at, item.updated_at,
        ),
        lambda: CheckpointRecord(
            item.identifier, item.metadata, item.payload, item.state, "c",
            None, item.created_at + timedelta(seconds=1), item.updated_at
        ),
        lambda: CheckpointSnapshot(
            "s", "bad", INSTANT, "0" * 64, 0
        ),
        lambda: CheckpointSnapshot(
            "s", item, INSTANT,
            DefaultCheckpointSerializer().digest(item), 1,
        ),
        lambda: CheckpointContext(
            "c", "bad", "namespace", "subject"
        ),
        lambda: CheckpointQuery(state="bad"),
        lambda: CheckpointQuery(
            created_from=INSTANT + timedelta(seconds=1),
            created_to=INSTANT,
        ),
        lambda: CheckpointQuery(descending=1),
        lambda: CheckpointCollection("bad"),
        lambda: CheckpointCollection(("bad",)),
        lambda: CheckpointCollection((item,), total=0),
        lambda: CheckpointResult(True, "bad"),
        lambda: CheckpointResult(
            True, CheckpointOperation.INSPECT, checkpoint="bad"
        ),
        lambda: CheckpointResult(
            True, CheckpointOperation.INSPECT, snapshot="bad"
        ),
        lambda: CheckpointResult(
            True, CheckpointOperation.INSPECT, collection="bad"
        ),
    )
    for call in invalid_calls:
        with pytest.raises(CheckpointException):
            call()
    assert list(CheckpointCollection((item,))) == [item]
    with pytest.raises(CheckpointSerializationError):
        CheckpointRecord.from_json(b"\xff")
    with pytest.raises(CheckpointSerializationError):
        CheckpointRecord.from_json("[]")
    with pytest.raises(CheckpointSerializationError):
        CheckpointPayload.from_dict({
            "schema_version": "1.0",
            "model": "checkpoint_payload",
            "content_type": "json",
            "encoding": "utf-8",
            "data": {"$binary": "AA==", "$encoding": "hex"},
            "size": 1,
            "sha256": "0" * 64,
        })
    for binary in (123, "***"):
        envelope = {
            "schema_version": "1.0",
            "model": "checkpoint_payload",
            "content_type": "json",
            "encoding": "utf-8",
            "data": {"$binary": binary, "$encoding": "base64"},
            "size": 1,
            "sha256": "0" * 64,
        }
        with pytest.raises(CheckpointSerializationError):
            CheckpointPayload.from_dict(envelope)


def test_additional_serializer_validator_and_error_branches(storage) -> None:
    serializer = DefaultCheckpointSerializer()
    validator = CheckpointValidator()
    with pytest.raises(CheckpointSerializationError):
        serializer.serialize("bad")
    with pytest.raises(CheckpointSerializationError):
        serializer.deserialize("bad")
    with pytest.raises(CheckpointSerializationError):
        serializer.deserialize(b"[]")
    corrupted = record().to_dict()
    corrupted["payload"]["sha256"] = "0" * 64
    canonical = json.dumps(
        corrupted,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    with pytest.raises(CheckpointIntegrityError):
        serializer.deserialize(canonical)
    for method, value in (
        (validator.validate_identifier, "bad"),
        (validator.validate_metadata, "bad"),
        (validator.validate_payload, "bad"),
        (validator.validate_record, "bad"),
        (validator.validate_snapshot, "bad"),
        (validator.validate_query, "bad"),
        (validator.validate_collection, "bad"),
        (validator.validate_result, "bad"),
        (validator.validate_context, "bad"),
    ):
        with pytest.raises(CheckpointValidationError):
            method(value)
    complete = CheckpointResult(
        True,
        CheckpointOperation.INSPECT,
        checkpoint=record(),
        snapshot=CheckpointSnapshot.capture("s", record(), INSTANT),
        collection=CheckpointCollection((record(),)),
    )
    assert validator.validate_result(complete) is complete
    assert validator.validate_storage(storage) is storage
    with pytest.raises(CheckpointValidationError):
        validator.validate_storage(object())
    for kwargs in (
        {"message": ""},
        {"message": "x", "code": ""},
        {"message": "x", "checkpoint_id": ""},
        {"message": "x", "details": "bad"},
    ):
        with pytest.raises(ValueError):
            CheckpointException(**kwargs)


class CallbackStorage(Storage):
    """Minimal Storage port test double with callback-controlled behavior."""

    def __init__(self, callback):
        self.callback = callback
        self._descriptor = StorageDescriptor(
            identifier="callback.storage",
            metadata=StorageMetadata("Callback", "Test double", "1.0"),
            capabilities=StorageCapabilities(tuple(StorageOperation)),
        )

    @property
    def descriptor(self) -> StorageDescriptor:
        return self._descriptor

    def execute(self, session):
        return self.callback(session)


def storage_result(session, *, success=True, metadata=None, message=None):
    """Build a result compatible with one callback session."""
    return StorageResult(
        storage_id="callback.storage",
        operation=session.context.operation,
        success=success,
        message=message,
        metadata={} if metadata is None else metadata,
    )


def test_repository_port_failure_chaining_and_result_validation() -> None:
    def raises_storage(session):
        raise StorageException("provider failed")

    def raises_unexpected(session):
        raise RuntimeError("provider failed")

    for callback, cause in (
        (raises_storage, StorageException),
        (raises_unexpected, RuntimeError),
    ):
        repository = StorageCheckpointRepository(CallbackStorage(callback))
        with pytest.raises(CheckpointStorageError) as captured:
            repository.restore(record().identifier)
        assert isinstance(captured.value.__cause__, cause)

    invalid_callbacks = (
        lambda session: object(),
        lambda session: StorageResult(
            "callback.storage",
            StorageOperation.WRITE,
            True,
            metadata={"exists": False},
        ),
        lambda session: storage_result(session, metadata={}),
    )
    for callback in invalid_callbacks:
        repository = StorageCheckpointRepository(CallbackStorage(callback))
        with pytest.raises(CheckpointStorageError):
            repository.restore(record().identifier)


def test_repository_read_content_identity_and_storage_failures() -> None:
    serializer = DefaultCheckpointSerializer()
    item = record(state=CheckpointState.STORED)

    def callback_for(content):
        def callback(session):
            if session.context.operation is StorageOperation.EXISTS:
                return storage_result(session, metadata={"exists": True})
            if session.context.operation is StorageOperation.READ:
                return storage_result(session, metadata=content)
            return storage_result(session)
        return callback

    for content in ({}, {"content_base64": "***"}):
        repository = StorageCheckpointRepository(
            CallbackStorage(callback_for(content))
        )
        with pytest.raises(CheckpointStorageError):
            repository.restore(item.identifier)
    other = record(
        checkpoint_id="other", state=CheckpointState.STORED
    )
    encoded = __import__("base64").b64encode(
        serializer.serialize(other)
    ).decode("ascii")
    repository = StorageCheckpointRepository(
        CallbackStorage(
            callback_for({"content_base64": encoded})
        )
    )
    with pytest.raises(CheckpointStorageError):
        repository.restore(item.identifier)

    def write_failure(session):
        if session.context.operation is StorageOperation.EXISTS:
            return storage_result(session, metadata={"exists": False})
        return storage_result(
            session, success=False, message="write rejected"
        )

    failed = StorageCheckpointRepository(
        CallbackStorage(write_failure)
    ).store(item)
    assert not failed.success
    assert failed.error_code == "checkpoint_storage_error"


def test_engine_dependency_clock_payload_and_supersede_validation(storage) -> None:
    for repository in (object(),):
        with pytest.raises(CheckpointValidationError):
            DefaultCheckpointEngine(repository)
    repository = StorageCheckpointRepository(storage)
    engine = DefaultCheckpointEngine(
        repository,
        clock=lambda: INSTANT.replace(tzinfo=None),
    )
    with pytest.raises(CheckpointValidationError):
        engine.create(context(), metadata(), {})
    good = DefaultCheckpointEngine(
        repository,
        clock=lambda: INSTANT,
        id_factory=lambda: "generated",
    )
    payload = CheckpointPayload("application/json", "utf-8", {"x": 1})
    created = good.create(
        context(), metadata(), payload, checkpoint_id="explicit"
    )
    assert created.checkpoint.payload is payload
    first = record(state=CheckpointState.STORED)
    with pytest.raises(CheckpointValidationError):
        good.supersede(first, first)
    unrelated = record(
        checkpoint_id="other",
        sequence=0,
        state=CheckpointState.STORED,
    )
    with pytest.raises(CheckpointValidationError):
        good.supersede(first, unrelated)
    no_parent = record(
        checkpoint_id="other",
        sequence=1,
        state=CheckpointState.STORED,
    )
    with pytest.raises(CheckpointValidationError):
        good.supersede(first, no_parent)
