"""Canonical exception for the storage abstraction foundation."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from cko.core.exceptions import CKOError


class StorageException(CKOError):
    """Report a storage contract, validation, or lifecycle violation."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "storage_error",
        storage_id: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        normalized = message.strip() if isinstance(message, str) else ""
        normalized_code = code.strip() if isinstance(code, str) else ""
        if not normalized:
            raise ValueError("message must be a non-empty string")
        if not normalized_code:
            raise ValueError("code must be a non-empty string")
        if storage_id is not None:
            storage_id = storage_id.strip()
            if not storage_id:
                raise ValueError("storage_id must be non-empty when provided")
        if details is not None and not isinstance(details, Mapping):
            raise ValueError("details must be a mapping when provided")
        self.code = normalized_code
        self.storage_id = storage_id
        self.details = MappingProxyType(dict(details or {}))
        super().__init__(normalized)

    def to_dict(self) -> dict[str, object]:
        """Return a serializable representation without implementation data."""
        return {
            "code": self.code,
            "storage_id": self.storage_id,
            "message": str(self),
            "details": dict(self.details),
        }


__all__ = ["StorageException"]
