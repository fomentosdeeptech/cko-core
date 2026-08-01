"""Typed failures for the Knowledge Relationship foundation."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from cko.core.exceptions import CKOError


class RelationshipError(CKOError):
    """Base failure raised by the relationship foundation."""

    default_code = "relationship_error"

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
        return {
            "code": self.code,
            "details": dict(self.details),
            "message": str(self),
            "model": self.model,
        }


class RelationshipValidationError(RelationshipError):
    default_code = "relationship_validation_error"


class RelationshipSerializationError(RelationshipError):
    default_code = "relationship_serialization_error"


class RelationshipFactoryError(RelationshipError):
    default_code = "relationship_factory_error"


class RelationshipIdentityError(RelationshipValidationError):
    default_code = "relationship_identity_error"


class RelationshipConstraintError(RelationshipValidationError):
    default_code = "relationship_constraint_error"


class RelationshipEvidenceError(RelationshipValidationError):
    default_code = "relationship_evidence_error"


__all__ = [
    "RelationshipConstraintError", "RelationshipError",
    "RelationshipEvidenceError", "RelationshipFactoryError",
    "RelationshipIdentityError", "RelationshipSerializationError",
    "RelationshipValidationError",
]
