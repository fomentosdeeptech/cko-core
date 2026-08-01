"""Stable exception hierarchy and error codes for provenance."""

from __future__ import annotations

from typing import Mapping

from cko.core.exceptions import CKOError


class ProvenanceError(CKOError):
    """Root for all explicitly emitted provenance failures."""

    def __init__(
        self,
        code: str,
        model: str,
        field: str,
        detail: str,
        *,
        details: Mapping[str, object] | None = None,
    ) -> None:
        self.code = code
        self.model = model
        self.field = field
        self.detail = detail
        self.details = dict(details or {})
        super().__init__(f"{code}:{model}:{field}:{detail}")


class ProvenanceValidationError(ProvenanceError, ValueError):
    """A public value violates a closed provenance invariant."""


class ProvenanceSerializationError(ProvenanceError):
    """A payload violates the closed canonical envelope."""


class ProvenanceFactoryError(ProvenanceError):
    """An aggregate was constructed outside its factory boundary."""


class ProvenanceIdentityError(ProvenanceValidationError):
    """A UUID or identity payload is invalid."""


class ProvenanceVersionError(ProvenanceValidationError):
    """A logical version or revision is invalid."""


class ProvenanceDigestError(ProvenanceValidationError):
    """A SHA-256 value or recomputation is invalid."""


class ProvenanceChainError(ProvenanceValidationError):
    """A supplied finite statement graph is invalid."""


__all__ = [
    "ProvenanceChainError",
    "ProvenanceDigestError",
    "ProvenanceError",
    "ProvenanceFactoryError",
    "ProvenanceIdentityError",
    "ProvenanceSerializationError",
    "ProvenanceValidationError",
    "ProvenanceVersionError",
]
