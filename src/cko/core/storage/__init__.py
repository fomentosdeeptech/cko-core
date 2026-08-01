"""Canonical storage abstraction foundation for the CKO CORE SDK."""

from .contracts import Storage
from .errors import StorageException
from .factory import StorageFactory
from .models import (
    STORAGE_SCHEMA_VERSION,
    STORAGE_VERSION,
    StorageCapabilities,
    StorageContext,
    StorageDescriptor,
    StorageLocation,
    StorageMetadata,
    StorageObject,
    StorageOperation,
    StorageResult,
    StorageSession,
    StorageSessionState,
)
from .registry import StorageConstructor, StorageRegistry
from .validator import StorageValidator

__all__ = [
    "STORAGE_SCHEMA_VERSION",
    "STORAGE_VERSION",
    "Storage",
    "StorageCapabilities",
    "StorageConstructor",
    "StorageContext",
    "StorageDescriptor",
    "StorageException",
    "StorageFactory",
    "StorageLocation",
    "StorageMetadata",
    "StorageObject",
    "StorageOperation",
    "StorageRegistry",
    "StorageResult",
    "StorageSession",
    "StorageSessionState",
    "StorageValidator",
]
