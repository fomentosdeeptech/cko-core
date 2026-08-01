"""Instance-scoped registry for abstract storage providers."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from types import MappingProxyType
from typing import Mapping, TypeAlias

from cko.core.logging import get_logger

from .contracts import Storage
from .errors import StorageException
from .models import StorageDescriptor
from .validator import StorageValidator


StorageConstructor: TypeAlias = Callable[[], Storage]


class StorageRegistry:
    """Register storage constructors without global state or technology coupling."""

    def __init__(self, validator: StorageValidator | None = None) -> None:
        self._validator = validator or StorageValidator()
        if not isinstance(self._validator, StorageValidator):
            raise StorageException("validator must be StorageValidator")
        self._registrations: dict[
            str, tuple[StorageDescriptor, StorageConstructor]
        ] = {}
        self._logger = get_logger("core.storage.registry")

    def register(
        self, descriptor: StorageDescriptor, constructor: StorageConstructor
    ) -> None:
        """Register a validated descriptor and its zero-argument constructor."""
        validated = self._validator.validate_descriptor(descriptor)
        if not callable(constructor):
            raise StorageException("constructor must be callable")
        identifier = validated.identifier
        if identifier in self._registrations:
            raise StorageException(
                f"storage is already registered: {identifier}",
                code="duplicate_storage",
                storage_id=identifier,
            )
        self._registrations[identifier] = (validated, constructor)
        self._logger.info(
            "storage_registered",
            extra={
                "event": "storage_registered",
                "context": {"storage_id": identifier},
            },
        )

    def get(self, identifier: str) -> StorageDescriptor:
        """Return the descriptor registered under an identifier."""
        normalized = self._identifier(identifier)
        try:
            return self._registrations[normalized][0]
        except KeyError as error:
            raise StorageException(
                f"storage is not registered: {normalized}",
                code="storage_not_found",
                storage_id=normalized,
            ) from error

    def constructor(self, identifier: str) -> StorageConstructor:
        """Return the constructor registered under an identifier."""
        normalized = self._identifier(identifier)
        try:
            return self._registrations[normalized][1]
        except KeyError as error:
            raise StorageException(
                f"storage is not registered: {normalized}",
                code="storage_not_found",
                storage_id=normalized,
            ) from error

    def descriptors(self) -> Sequence[StorageDescriptor]:
        """Return an identifier-ordered immutable descriptor snapshot."""
        return tuple(
            self._registrations[key][0] for key in sorted(self._registrations)
        )

    def snapshot(self) -> Mapping[str, StorageDescriptor]:
        """Return a read-only identifier-ordered registry snapshot."""
        return MappingProxyType(
            {
                key: self._registrations[key][0]
                for key in sorted(self._registrations)
            }
        )

    def __len__(self) -> int:
        return len(self._registrations)

    def __iter__(self) -> Iterator[StorageDescriptor]:
        return iter(self.descriptors())

    @staticmethod
    def _identifier(value: object) -> str:
        if not isinstance(value, str) or not value.strip():
            raise StorageException("identifier must be a non-empty string")
        return value.strip()


__all__ = ["StorageConstructor", "StorageRegistry"]
