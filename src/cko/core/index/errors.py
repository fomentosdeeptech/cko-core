"""Stable exception hierarchy for the Knowledge Index Foundation."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from cko.core.exceptions import CKOError


class IndexError(CKOError):
    default_code = "index_error"

    def __init__(self, message: str, *, code: str | None = None,
                 model: str | None = None,
                 details: Mapping[str, object] | None = None) -> None:
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message must be a non-empty string")
        super().__init__(message.strip())
        self.code = (code or self.default_code).strip()
        self.model = model.strip() if isinstance(model, str) else None
        self.details = MappingProxyType(dict(details or {}))

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": str(self), "model": self.model,
                "details": dict(self.details)}


class IndexValidationError(IndexError, ValueError):
    default_code = "index_validation_error"


class IndexSerializationError(IndexError):
    default_code = "index_serialization_error"


class IndexFactoryError(IndexError):
    default_code = "index_factory_error"


class IndexIdentityError(IndexValidationError):
    default_code = "index_identity_error"


class IndexDefinitionError(IndexValidationError):
    default_code = "index_definition_error"


class IndexOperationError(IndexError):
    default_code = "index_operation_error"


class IndexConsistencyError(IndexValidationError):
    default_code = "index_consistency_error"


class IndexQueryError(IndexValidationError):
    default_code = "index_query_error"


__all__ = ["IndexConsistencyError", "IndexDefinitionError", "IndexError",
           "IndexFactoryError", "IndexIdentityError", "IndexOperationError",
           "IndexQueryError", "IndexSerializationError", "IndexValidationError"]
