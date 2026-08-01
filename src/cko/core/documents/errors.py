"""Typed failures for the canonical document model."""

from cko.core.exceptions import CKOError


class DocumentError(CKOError):
    """Base failure raised by the document canonical model."""


class DocumentValidationError(DocumentError):
    """Report an invalid document model or aggregate invariant."""


class DocumentSerializationError(DocumentError):
    """Report malformed or non-canonical serialized document data."""


class DocumentFactoryError(DocumentError):
    """Report a failure at the mandatory document construction boundary."""


__all__ = [
    "DocumentError", "DocumentFactoryError", "DocumentSerializationError",
    "DocumentValidationError",
]
