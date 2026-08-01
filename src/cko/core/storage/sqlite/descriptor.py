"""Public descriptors for the SQLite storage adapter."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Mapping, Self

from cko.core.connectors import (
    ConnectorCapabilities,
    ConnectorDescriptor,
    ConnectorMetadata,
)
from cko.core.storage import (
    StorageCapabilities,
    StorageDescriptor,
    StorageException,
    StorageMetadata,
    StorageOperation,
)


SQLITE_SCHEMA_VERSION = "1.0"
SQLITE_VERSION = "1.0.0"
SQLITE_IDENTIFIER = "cko.storage.sqlite"
SQLITE_OPERATIONS = (
    "copy",
    "create",
    "delete",
    "exists",
    "list",
    "metadata",
    "move",
    "read",
    "write",
)


def _storage_descriptor() -> StorageDescriptor:
    return StorageDescriptor(
        identifier=SQLITE_IDENTIFIER,
        metadata=StorageMetadata(
            name="SQLite Storage",
            description="Standard-library SQLite structured storage adapter",
            version=SQLITE_VERSION,
            labels={"technology": "sqlite"},
        ),
        capabilities=StorageCapabilities(
            operations=tuple(StorageOperation),
            supports_atomic_write=True,
            supports_streaming=False,
            supports_transactions=True,
        ),
    )


def _connector_descriptor() -> ConnectorDescriptor:
    return ConnectorDescriptor(
        identifier=SQLITE_IDENTIFIER,
        metadata=ConnectorMetadata(
            name="SQLite Connector",
            description="Standard-library SQLite structured storage connector",
            version=SQLITE_VERSION,
            labels={"technology": "sqlite"},
        ),
        capabilities=ConnectorCapabilities(
            operations=SQLITE_OPERATIONS,
            features=(
                "deterministic_json",
                "logical_location",
                "prepared_statements",
                "transactions",
            ),
            supports_streaming=False,
        ),
    )


@dataclass(frozen=True, slots=True)
class SQLiteDescriptor:
    """Pair the public Connector and Storage descriptors of the adapter."""

    storage_descriptor: StorageDescriptor = field(
        default_factory=_storage_descriptor
    )
    connector_descriptor: ConnectorDescriptor = field(
        default_factory=_connector_descriptor
    )
    schema_version: str = SQLITE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.storage_descriptor, StorageDescriptor):
            raise StorageException(
                "storage_descriptor must be StorageDescriptor"
            )
        if not isinstance(self.connector_descriptor, ConnectorDescriptor):
            raise StorageException(
                "connector_descriptor must be ConnectorDescriptor"
            )
        if (
            self.storage_descriptor.identifier
            != self.connector_descriptor.identifier
        ):
            raise StorageException("SQLite descriptor identifiers differ")
        if self.schema_version != SQLITE_SCHEMA_VERSION:
            raise StorageException("unsupported SQLiteDescriptor version")

    @property
    def storage(self) -> StorageDescriptor:
        """Return the canonical Storage descriptor."""
        return self.storage_descriptor

    @property
    def connector(self) -> ConnectorDescriptor:
        """Return the canonical Connector descriptor."""
        return self.connector_descriptor

    def to_dict(self) -> dict[str, object]:
        """Serialize the descriptor pair deterministically."""
        return {
            "schema_version": self.schema_version,
            "model": "sqlite_descriptor",
            "storage_descriptor": self.storage_descriptor.to_dict(),
            "connector_descriptor": self.connector_descriptor.to_dict(),
        }

    def to_json(self) -> str:
        """Serialize the descriptor pair to deterministic JSON."""
        return json.dumps(
            self.to_dict(),
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict SQLite descriptor envelope."""
        expected = {
            "schema_version",
            "model",
            "storage_descriptor",
            "connector_descriptor",
        }
        if not isinstance(payload, Mapping) or set(payload) != expected:
            raise StorageException("invalid sqlite_descriptor envelope")
        if (
            payload.get("schema_version") != SQLITE_SCHEMA_VERSION
            or payload.get("model") != "sqlite_descriptor"
        ):
            raise StorageException("invalid sqlite_descriptor envelope")
        storage = payload["storage_descriptor"]
        connector = payload["connector_descriptor"]
        if not isinstance(storage, Mapping) or not isinstance(connector, Mapping):
            raise StorageException("invalid SQLite descriptor models")
        return cls(
            storage_descriptor=StorageDescriptor.from_dict(storage),
            connector_descriptor=ConnectorDescriptor.from_dict(connector),
            schema_version=str(payload["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize a SQLite descriptor from strict JSON."""
        try:
            decoded = json.loads(payload)
        except (TypeError, json.JSONDecodeError) as error:
            raise StorageException("SQLite descriptor JSON is invalid") from error
        if not isinstance(decoded, Mapping):
            raise StorageException("SQLite descriptor JSON is invalid")
        return cls.from_dict(decoded)


__all__ = [
    "SQLITE_IDENTIFIER",
    "SQLITE_OPERATIONS",
    "SQLITE_SCHEMA_VERSION",
    "SQLITE_VERSION",
    "SQLiteDescriptor",
]
