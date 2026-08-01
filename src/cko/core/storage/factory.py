"""Generic factory for registered storage abstractions."""

from __future__ import annotations

from cko.core.logging import get_logger

from .contracts import Storage
from .errors import StorageException
from .registry import StorageRegistry
from .validator import StorageValidator


class StorageFactory:
    """Instantiate registered storage without knowing concrete technologies."""

    def __init__(
        self,
        registry: StorageRegistry,
        validator: StorageValidator | None = None,
    ) -> None:
        if not isinstance(registry, StorageRegistry):
            raise StorageException("registry must be StorageRegistry")
        self._registry = registry
        self._validator = validator or StorageValidator()
        if not isinstance(self._validator, StorageValidator):
            raise StorageException("validator must be StorageValidator")
        self._logger = get_logger("core.storage.factory")

    def create(self, identifier: str) -> Storage:
        """Create and validate storage from its registered constructor."""
        descriptor = self._registry.get(identifier)
        constructor = self._registry.constructor(identifier)
        try:
            storage = constructor()
        except StorageException:
            raise
        except Exception as error:
            raise StorageException(
                "storage construction failed",
                code="storage_creation_failed",
                storage_id=descriptor.identifier,
            ) from error
        self._validator.validate_storage(storage, descriptor)
        self._logger.info(
            "storage_created",
            extra={
                "event": "storage_created",
                "context": {"storage_id": descriptor.identifier},
            },
        )
        return storage


__all__ = ["StorageFactory"]
