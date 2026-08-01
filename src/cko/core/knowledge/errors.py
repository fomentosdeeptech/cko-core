"""Typed failures for the canonical Knowledge Object foundation."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from cko.core.exceptions import CKOError


class KnowledgeError(CKOError):
    """Base failure raised by the Knowledge Object foundation."""

    default_code = "knowledge_error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        model: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        normalized = message.strip() if isinstance(message, str) else ""
        normalized_code = self.default_code if code is None else (
            code.strip() if isinstance(code, str) else ""
        )
        if not normalized:
            raise ValueError("message must be a non-empty string")
        if not normalized_code:
            raise ValueError("code must be a non-empty string")
        if model is not None:
            model = model.strip() if isinstance(model, str) else ""
            if not model:
                raise ValueError("model must be non-empty when provided")
        if details is not None and not isinstance(details, Mapping):
            raise ValueError("details must be a mapping when provided")
        self.code = normalized_code
        self.model = model
        self.details = MappingProxyType(dict(details or {}))
        super().__init__(normalized)

    def to_dict(self) -> dict[str, object]:
        """Return a safe representation of the failure."""
        return {
            "code": self.code,
            "details": dict(self.details),
            "message": str(self),
            "model": self.model,
        }


class KnowledgeValidationError(KnowledgeError):
    """Report an invalid model or cross-model invariant."""

    default_code = "knowledge_validation_error"


class KnowledgeSerializationError(KnowledgeError):
    """Report malformed, unknown, or non-canonical serialization."""

    default_code = "knowledge_serialization_error"


class KnowledgeFactoryError(KnowledgeError):
    """Report an invalid or unauthorized object construction."""

    default_code = "knowledge_factory_error"


class KnowledgeVersionError(KnowledgeValidationError):
    """Report an invalid version lineage or integrity hash."""

    default_code = "knowledge_version_error"


class KnowledgeRelationshipError(KnowledgeValidationError):
    """Report an invalid relationship declaration."""

    default_code = "knowledge_relationship_error"


__all__ = [
    "KnowledgeError",
    "KnowledgeFactoryError",
    "KnowledgeRelationshipError",
    "KnowledgeSerializationError",
    "KnowledgeValidationError",
    "KnowledgeVersionError",
]
