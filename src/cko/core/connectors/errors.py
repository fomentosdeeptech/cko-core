"""Canonical exception for the connector abstraction foundation."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from cko.core.exceptions import CKOError


class ConnectorException(CKOError):
    """Report a connector contract or lifecycle violation."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "connector_error",
        connector_id: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        normalized = message.strip() if isinstance(message, str) else ""
        normalized_code = code.strip() if isinstance(code, str) else ""
        if not normalized:
            raise ValueError("message must be a non-empty string")
        if not normalized_code:
            raise ValueError("code must be a non-empty string")
        if connector_id is not None:
            connector_id = connector_id.strip()
            if not connector_id:
                raise ValueError("connector_id must be non-empty when provided")
        self.code = normalized_code
        self.connector_id = connector_id
        self.details = MappingProxyType(dict(details or {}))
        super().__init__(normalized)

    def to_dict(self) -> dict[str, object]:
        """Return a serializable representation without implementation data."""
        return {
            "code": self.code,
            "connector_id": self.connector_id,
            "message": str(self),
            "details": dict(self.details),
        }


__all__ = ["ConnectorException"]
