"""Stable exception hierarchy for the Knowledge Corpus Foundation."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from cko.core.exceptions import CKOError


class CorpusError(CKOError):
    default_code = "corpus_error"

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


class CorpusValidationError(CorpusError, ValueError):
    default_code = "corpus_validation_error"


class CorpusIdentityError(CorpusValidationError):
    default_code = "corpus_identity_error"


class CorpusReferenceError(CorpusValidationError):
    default_code = "corpus_reference_error"


class CorpusCategoryError(CorpusReferenceError):
    default_code = "corpus_category_error"


class DuplicateCorpusMemberError(CorpusValidationError):
    default_code = "duplicate_corpus_member_error"


class CorpusManifestError(CorpusValidationError):
    default_code = "corpus_manifest_error"


class CorpusVersionError(CorpusValidationError):
    default_code = "corpus_version_error"


class CorpusDigestError(CorpusValidationError):
    default_code = "corpus_digest_error"


class CorpusSerializationError(CorpusError):
    default_code = "corpus_serialization_error"


class CorpusFactoryError(CorpusError):
    default_code = "corpus_factory_error"


class CorpusOperationError(CorpusError):
    default_code = "corpus_operation_error"


__all__ = [
    "CorpusCategoryError", "CorpusDigestError", "CorpusError",
    "CorpusFactoryError", "CorpusIdentityError", "CorpusManifestError",
    "CorpusOperationError", "CorpusReferenceError", "CorpusSerializationError",
    "CorpusValidationError", "CorpusVersionError", "DuplicateCorpusMemberError",
]
