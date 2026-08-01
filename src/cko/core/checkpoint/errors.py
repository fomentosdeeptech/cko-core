"""Typed errors for the canonical checkpoint foundation."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from cko.core.exceptions import CKOError


class CheckpointException(CKOError):
    """Base error for checkpoint contracts and operations."""

    default_code = "checkpoint_error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        checkpoint_id: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        normalized = message.strip() if isinstance(message, str) else ""
        normalized_code = (
            self.default_code if code is None else code.strip()
            if isinstance(code, str) else ""
        )
        if not normalized:
            raise ValueError("message must be a non-empty string")
        if not normalized_code:
            raise ValueError("code must be a non-empty string")
        if checkpoint_id is not None:
            checkpoint_id = checkpoint_id.strip()
            if not checkpoint_id:
                raise ValueError(
                    "checkpoint_id must be non-empty when provided"
                )
        if details is not None and not isinstance(details, Mapping):
            raise ValueError("details must be a mapping when provided")
        self.code = normalized_code
        self.checkpoint_id = checkpoint_id
        self.details = MappingProxyType(dict(details or {}))
        super().__init__(normalized)

    def to_dict(self) -> dict[str, object]:
        """Return a safe serializable representation of the error."""
        return {
            "code": self.code,
            "checkpoint_id": self.checkpoint_id,
            "message": str(self),
            "details": dict(self.details),
        }


class CheckpointValidationError(CheckpointException):
    """Report a checkpoint model or contract validation failure."""

    default_code = "checkpoint_validation_error"


class CheckpointSerializationError(CheckpointException):
    """Report invalid or unsupported checkpoint serialization."""

    default_code = "checkpoint_serialization_error"


class CheckpointIntegrityError(CheckpointException):
    """Report a digest or canonical-size mismatch."""

    default_code = "checkpoint_integrity_error"


class CheckpointNotFoundError(CheckpointException):
    """Report a checkpoint that does not exist."""

    default_code = "checkpoint_not_found"


class CheckpointConflictError(CheckpointException):
    """Report an incompatible checkpoint already stored."""

    default_code = "checkpoint_conflict"


class CheckpointStorageError(CheckpointException):
    """Report a failure returned by or raised from the Storage port."""

    default_code = "checkpoint_storage_error"


class CheckpointStateError(CheckpointException):
    """Report an invalid checkpoint lifecycle transition."""

    default_code = "checkpoint_state_error"


__all__ = [
    "CheckpointConflictError",
    "CheckpointException",
    "CheckpointIntegrityError",
    "CheckpointNotFoundError",
    "CheckpointSerializationError",
    "CheckpointStateError",
    "CheckpointStorageError",
    "CheckpointValidationError",
]
