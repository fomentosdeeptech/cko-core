"""Canonical connector abstraction foundation for the CKO CORE SDK."""

from .contracts import Connector
from .errors import ConnectorException
from .factory import ConnectorFactory
from .models import (
    CONNECTOR_SCHEMA_VERSION,
    CONNECTOR_VERSION,
    ConnectorCapabilities,
    ConnectorContext,
    ConnectorDescriptor,
    ConnectorMetadata,
    ConnectorResult,
    ConnectorSession,
    ConnectorSessionState,
)
from .registry import ConnectorConstructor, ConnectorRegistry
from .validator import ConnectorValidator

__all__ = [
    "CONNECTOR_SCHEMA_VERSION",
    "CONNECTOR_VERSION",
    "Connector",
    "ConnectorCapabilities",
    "ConnectorConstructor",
    "ConnectorContext",
    "ConnectorDescriptor",
    "ConnectorException",
    "ConnectorFactory",
    "ConnectorMetadata",
    "ConnectorRegistry",
    "ConnectorResult",
    "ConnectorSession",
    "ConnectorSessionState",
    "ConnectorValidator",
]
