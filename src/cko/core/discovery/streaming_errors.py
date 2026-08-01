"""Public errors for the Discovery streaming and batch foundation."""

from __future__ import annotations

from .errors import DiscoveryError


class InvalidDiscoveryStreamError(DiscoveryError, ValueError):
    """Raised when a stream identity or configuration is inconsistent."""


class DiscoveryStreamTransitionError(DiscoveryError, RuntimeError):
    """Raised when a stream receives an invalid state transition."""


class InvalidBatchSequenceError(DiscoveryError, ValueError):
    """Raised when a batch does not follow the expected logical sequence."""


class DuplicateBatchError(InvalidBatchSequenceError):
    """Raised when a batch sequence or identity has already been observed."""


class InvalidBatchCursorError(DiscoveryError, ValueError):
    """Raised when a logical batch cursor violates its versioned schema."""


class InvalidBatchAcknowledgementError(DiscoveryError, ValueError):
    """Raised when a batch acknowledgement is incomplete or inconsistent."""


class BatchProducerError(DiscoveryError, RuntimeError):
    """Raised when an injected batch producer fails its public contract."""


class BatchConsumerError(DiscoveryError, RuntimeError):
    """Raised when an injected batch consumer fails its public contract."""


class BackpressureViolationError(DiscoveryError, RuntimeError):
    """Raised when a batch violates the declared flow-control policy."""


__all__ = [
    "BackpressureViolationError",
    "BatchConsumerError",
    "BatchProducerError",
    "DiscoveryStreamTransitionError",
    "DuplicateBatchError",
    "InvalidBatchAcknowledgementError",
    "InvalidBatchCursorError",
    "InvalidBatchSequenceError",
    "InvalidDiscoveryStreamError",
]
