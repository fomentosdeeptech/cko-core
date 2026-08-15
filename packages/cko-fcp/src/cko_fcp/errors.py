"""Semantic error taxonomy for the external FCP foundation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ErrorDetail:
    code: str
    category: str
    retryable: bool
    safe_message: str
    correlation_id: str | None = None


class FCPError(Exception):
    code = "FCP_CONTRACT_VIOLATION"
    category = "contract_violation"
    retryable = False

    def __init__(self, safe_message: str, *, correlation_id: str | None = None) -> None:
        self.detail = ErrorDetail(
            self.code, self.category, self.retryable, safe_message, correlation_id
        )
        super().__init__(safe_message)


class ValidationError(FCPError):
    code = "FCP_INVALID_INPUT"
    category = "validation_failure"


class IdentityError(ValidationError):
    category = "invalid_identity"


class InvalidRecordError(ValidationError):
    category = "invalid_record"


class InvalidEnvelopeError(ValidationError):
    category = "invalid_envelope"


class InvalidLifecycleTransitionError(FCPError):
    code = "FCP_ILLEGAL_TRANSITION"
    category = "invalid_lifecycle_transition"


class UnsupportedVersionError(FCPError):
    code = "FCP_UNSUPPORTED_MAJOR"
    category = "unsupported_version"


class CapabilityAbsentError(FCPError):
    code = "FCP_CAPABILITY_ABSENT"
    category = "unsupported_capability"


class ContractViolationError(FCPError):
    category = "contract_violation"
