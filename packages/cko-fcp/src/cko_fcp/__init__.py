"""Public foundation for the independently distributed Federated Catalog Protocol."""

DISTRIBUTION_VERSION = "0.1.0"

from .contracts import (
    CapabilityProfile,
    NegotiatedProfile,
    OperationEnvelope,
    PageRequest,
    negotiate,
)
from .errors import (
    CapabilityAbsentError,
    ContractViolationError,
    FCPError,
    IdentityError,
    InvalidEnvelopeError,
    InvalidLifecycleTransitionError,
    InvalidRecordError,
    UnsupportedVersionError,
    ValidationError,
)
from .lifecycle import transition
from .models import (
    CatalogRecord,
    FCPVersion,
    Lifecycle,
    Maturity,
    Publication,
    RecordState,
    SourceIdentity,
    Trust,
    Visibility,
)
from .serialization import canonical_bytes, canonical_digest, canonical_json

__all__ = (
    "CapabilityAbsentError",
    "CapabilityProfile",
    "CatalogRecord",
    "ContractViolationError",
    "DISTRIBUTION_VERSION",
    "FCPError",
    "FCPVersion",
    "IdentityError",
    "InvalidEnvelopeError",
    "InvalidLifecycleTransitionError",
    "InvalidRecordError",
    "Lifecycle",
    "Maturity",
    "NegotiatedProfile",
    "OperationEnvelope",
    "PageRequest",
    "Publication",
    "RecordState",
    "SourceIdentity",
    "Trust",
    "UnsupportedVersionError",
    "ValidationError",
    "Visibility",
    "canonical_bytes",
    "canonical_digest",
    "canonical_json",
    "negotiate",
    "transition",
)
