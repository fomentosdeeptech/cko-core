"""Validation services for canonical connector contracts."""

from __future__ import annotations

from cko.core.logging import get_logger

from .contracts import Connector
from .errors import ConnectorException
from .models import (
    CONNECTOR_VERSION,
    ConnectorCapabilities,
    ConnectorContext,
    ConnectorDescriptor,
    ConnectorSession,
    ConnectorSessionState,
)


class ConnectorValidator:
    """Validate connector values and cross-contract invariants."""

    def __init__(self) -> None:
        self._logger = get_logger("core.connectors.validator")

    def _validated(self, component: str, connector_id: str | None = None) -> None:
        self._logger.info(
            "connector_validated",
            extra={
                "event": "connector_validated",
                "context": {
                    "component": component,
                    "connector_id": connector_id,
                },
            },
        )

    def validate_capabilities(
        self, capabilities: ConnectorCapabilities
    ) -> ConnectorCapabilities:
        """Validate a normalized connector capability declaration."""
        if not isinstance(capabilities, ConnectorCapabilities):
            raise ConnectorException(
                "capabilities must be ConnectorCapabilities",
                code="invalid_capabilities",
            )
        if not capabilities.operations:
            raise ConnectorException(
                "connector must declare at least one operation",
                code="invalid_capabilities",
            )
        self._validated("capabilities")
        return capabilities

    def validate_descriptor(
        self, descriptor: ConnectorDescriptor
    ) -> ConnectorDescriptor:
        """Validate descriptor identity, version, metadata, and capabilities."""
        if not isinstance(descriptor, ConnectorDescriptor):
            raise ConnectorException(
                "descriptor must be ConnectorDescriptor",
                code="invalid_descriptor",
            )
        if descriptor.contract_version != CONNECTOR_VERSION:
            raise ConnectorException(
                "unsupported connector contract version",
                code="unsupported_contract_version",
                connector_id=descriptor.identifier,
            )
        self.validate_capabilities(descriptor.capabilities)
        self._validated("descriptor", descriptor.identifier)
        return descriptor

    def validate_context(
        self,
        context: ConnectorContext,
        descriptor: ConnectorDescriptor | None = None,
    ) -> ConnectorContext:
        """Validate context structure and optional operation compatibility."""
        if not isinstance(context, ConnectorContext):
            raise ConnectorException(
                "context must be ConnectorContext",
                code="invalid_context",
            )
        if descriptor is not None:
            self.validate_descriptor(descriptor)
            if not descriptor.capabilities.supports(context.operation):
                raise ConnectorException(
                    f"unsupported connector operation: {context.operation}",
                    code="unsupported_operation",
                    connector_id=descriptor.identifier,
                )
        self._validated(
            "context", None if descriptor is None else descriptor.identifier
        )
        return context

    def validate_session(
        self,
        session: ConnectorSession,
        descriptor: ConnectorDescriptor | None = None,
    ) -> ConnectorSession:
        """Validate session identity, lifecycle, and optional descriptor binding."""
        if not isinstance(session, ConnectorSession):
            raise ConnectorException(
                "session must be ConnectorSession",
                code="invalid_session",
            )
        if descriptor is not None:
            self.validate_descriptor(descriptor)
            if session.connector_id != descriptor.identifier:
                raise ConnectorException(
                    "session connector identity does not match descriptor",
                    code="invalid_session",
                    connector_id=descriptor.identifier,
                )
            self.validate_context(session.context, descriptor)
        if (
            session.state is ConnectorSessionState.STARTED
            and session.finished_at is not None
        ):
            raise ConnectorException(
                "started session cannot have finished_at",
                code="invalid_session",
                connector_id=session.connector_id,
            )
        self._validated("session", session.connector_id)
        return session

    def validate_connector(
        self,
        connector: Connector,
        expected: ConnectorDescriptor | None = None,
    ) -> Connector:
        """Validate an instantiated connector against its registered contract."""
        if not isinstance(connector, Connector):
            raise ConnectorException(
                "factory did not create a Connector",
                code="invalid_connector",
            )
        descriptor = self.validate_descriptor(connector.descriptor)
        if expected is not None and descriptor != expected:
            raise ConnectorException(
                "connector descriptor does not match its registration",
                code="descriptor_mismatch",
                connector_id=expected.identifier,
            )
        self._validated("connector", descriptor.identifier)
        return connector


__all__ = ["ConnectorValidator"]
