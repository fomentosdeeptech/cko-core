"""Instance-scoped deterministic registry for connector abstractions."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from types import MappingProxyType
from typing import Mapping

from cko.core.logging import get_logger

from .contracts import Connector
from .errors import ConnectorException
from .models import ConnectorDescriptor
from .validator import ConnectorValidator


ConnectorConstructor = Callable[[], Connector]


class ConnectorRegistry:
    """Register constructors without global state or implementation knowledge."""

    def __init__(self, validator: ConnectorValidator | None = None) -> None:
        self._validator = validator or ConnectorValidator()
        if not isinstance(self._validator, ConnectorValidator):
            raise ConnectorException("validator must be ConnectorValidator")
        self._registrations: dict[
            str, tuple[ConnectorDescriptor, ConnectorConstructor]
        ] = {}
        self._logger = get_logger("core.connectors.registry")

    def register(
        self,
        descriptor: ConnectorDescriptor,
        constructor: ConnectorConstructor,
    ) -> None:
        """Register one unique descriptor and its zero-argument constructor."""
        self._validator.validate_descriptor(descriptor)
        if not callable(constructor):
            raise ConnectorException(
                "constructor must be callable",
                code="invalid_registration",
                connector_id=descriptor.identifier,
            )
        if descriptor.identifier in self._registrations:
            raise ConnectorException(
                f"connector already registered: {descriptor.identifier}",
                code="duplicate_connector",
                connector_id=descriptor.identifier,
            )
        self._registrations[descriptor.identifier] = (descriptor, constructor)
        self._logger.info(
            "connector_registered",
            extra={
                "event": "connector_registered",
                "context": {"connector_id": descriptor.identifier},
            },
        )

    def get(self, identifier: str) -> ConnectorDescriptor:
        """Return a registered descriptor by its stable identifier."""
        normalized = self._identifier(identifier)
        try:
            return self._registrations[normalized][0]
        except KeyError as error:
            raise ConnectorException(
                f"connector is not registered: {normalized}",
                code="connector_not_found",
                connector_id=normalized,
            ) from error

    def descriptors(self) -> Sequence[ConnectorDescriptor]:
        """Return an identifier-ordered immutable descriptor snapshot."""
        return tuple(
            self._registrations[key][0] for key in sorted(self._registrations)
        )

    def snapshot(self) -> Mapping[str, ConnectorDescriptor]:
        """Return a read-only identifier-ordered registry snapshot."""
        return MappingProxyType(
            {key: self._registrations[key][0]
             for key in sorted(self._registrations)}
        )

    def constructor(self, identifier: str) -> ConnectorConstructor:
        """Return the registered constructor for use by ConnectorFactory."""
        normalized = self._identifier(identifier)
        try:
            return self._registrations[normalized][1]
        except KeyError as error:
            raise ConnectorException(
                f"connector is not registered: {normalized}",
                code="connector_not_found",
                connector_id=normalized,
            ) from error

    def __len__(self) -> int:
        return len(self._registrations)

    def __iter__(self) -> Iterator[ConnectorDescriptor]:
        return iter(self.descriptors())

    @staticmethod
    def _identifier(value: object) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ConnectorException("identifier must be a non-empty string")
        return value.strip()


__all__ = ["ConnectorConstructor", "ConnectorRegistry"]
