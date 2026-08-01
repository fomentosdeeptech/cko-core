"""Generic factory for registered connector abstractions."""

from __future__ import annotations

from cko.core.logging import get_logger

from .contracts import Connector
from .errors import ConnectorException
from .registry import ConnectorRegistry
from .validator import ConnectorValidator


class ConnectorFactory:
    """Instantiate registered connectors without knowing concrete technologies."""

    def __init__(
        self,
        registry: ConnectorRegistry,
        validator: ConnectorValidator | None = None,
    ) -> None:
        if not isinstance(registry, ConnectorRegistry):
            raise ConnectorException("registry must be ConnectorRegistry")
        self._registry = registry
        self._validator = validator or ConnectorValidator()
        if not isinstance(self._validator, ConnectorValidator):
            raise ConnectorException("validator must be ConnectorValidator")
        self._logger = get_logger("core.connectors.factory")

    def create(self, identifier: str) -> Connector:
        """Create and validate one connector from its registered constructor."""
        descriptor = self._registry.get(identifier)
        constructor = self._registry.constructor(identifier)
        try:
            connector = constructor()
        except ConnectorException:
            raise
        except Exception as error:
            raise ConnectorException(
                "connector construction failed",
                code="connector_creation_failed",
                connector_id=descriptor.identifier,
            ) from error
        self._validator.validate_connector(connector, descriptor)
        self._logger.info(
            "connector_created",
            extra={
                "event": "connector_created",
                "context": {"connector_id": descriptor.identifier},
            },
        )
        return connector


__all__ = ["ConnectorFactory"]
