"""Public descriptors for the filesystem storage adapter."""

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


FILESYSTEM_SCHEMA_VERSION = "1.0"
FILESYSTEM_VERSION = "1.0.0"
FILESYSTEM_IDENTIFIER = "cko.storage.filesystem"
FILESYSTEM_OPERATIONS = (
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
        identifier=FILESYSTEM_IDENTIFIER,
        metadata=StorageMetadata(
            name="Filesystem Storage",
            description="Standard-library filesystem storage adapter",
            version=FILESYSTEM_VERSION,
            labels={"technology": "filesystem"},
        ),
        capabilities=StorageCapabilities(
            operations=tuple(StorageOperation),
            supports_atomic_write=False,
            supports_streaming=False,
            supports_transactions=False,
        ),
    )


def _connector_descriptor() -> ConnectorDescriptor:
    return ConnectorDescriptor(
        identifier=FILESYSTEM_IDENTIFIER,
        metadata=ConnectorMetadata(
            name="Filesystem Connector",
            description="Standard-library filesystem connector adapter",
            version=FILESYSTEM_VERSION,
            labels={"technology": "filesystem"},
        ),
        capabilities=ConnectorCapabilities(
            operations=FILESYSTEM_OPERATIONS,
            features=("binary_base64", "logical_location"),
            supports_streaming=False,
        ),
    )


@dataclass(frozen=True, slots=True)
class FilesystemDescriptor:
    """Pair the public Connector and Storage descriptors of the adapter."""

    storage_descriptor: StorageDescriptor = field(
        default_factory=_storage_descriptor
    )
    connector_descriptor: ConnectorDescriptor = field(
        default_factory=_connector_descriptor
    )
    schema_version: str = FILESYSTEM_SCHEMA_VERSION

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
            raise StorageException("filesystem descriptor identifiers differ")
        if self.schema_version != FILESYSTEM_SCHEMA_VERSION:
            raise StorageException("unsupported FilesystemDescriptor version")

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
            "model": "filesystem_descriptor",
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
        """Deserialize a strict filesystem descriptor envelope."""
        expected = {
            "schema_version",
            "model",
            "storage_descriptor",
            "connector_descriptor",
        }
        if not isinstance(payload, Mapping) or set(payload) != expected:
            raise StorageException("invalid filesystem_descriptor envelope")
        if (
            payload.get("schema_version") != FILESYSTEM_SCHEMA_VERSION
            or payload.get("model") != "filesystem_descriptor"
        ):
            raise StorageException("invalid filesystem_descriptor envelope")
        storage = payload["storage_descriptor"]
        connector = payload["connector_descriptor"]
        if not isinstance(storage, Mapping) or not isinstance(connector, Mapping):
            raise StorageException("invalid filesystem descriptor models")
        return cls(
            storage_descriptor=StorageDescriptor.from_dict(storage),
            connector_descriptor=ConnectorDescriptor.from_dict(connector),
            schema_version=str(payload["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize a filesystem descriptor from strict JSON."""
        try:
            decoded = json.loads(payload)
        except (TypeError, json.JSONDecodeError) as error:
            raise StorageException("filesystem descriptor JSON is invalid") from error
        if not isinstance(decoded, Mapping):
            raise StorageException("filesystem descriptor JSON is invalid")
        return cls.from_dict(decoded)


__all__ = [
    "FILESYSTEM_IDENTIFIER",
    "FILESYSTEM_OPERATIONS",
    "FILESYSTEM_SCHEMA_VERSION",
    "FILESYSTEM_VERSION",
    "FilesystemDescriptor",
]
