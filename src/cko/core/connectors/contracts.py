"""Technology-neutral connector port for the CKO CORE SDK."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import ConnectorDescriptor, ConnectorResult, ConnectorSession


class Connector(ABC):
    """Port implemented by future external-technology adapters."""

    @property
    @abstractmethod
    def descriptor(self) -> ConnectorDescriptor:
        """Return the immutable descriptor implemented by this connector."""

    @abstractmethod
    def execute(self, session: ConnectorSession) -> ConnectorResult:
        """Execute one logical operation for an already started session."""


__all__ = ["Connector"]
