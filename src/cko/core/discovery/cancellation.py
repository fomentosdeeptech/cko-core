"""Infrastructure-neutral cooperative cancellation for Discovery."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from cko.core.identity import CanonicalId
from cko.core.logging import get_logger
from cko.core.utils import require_non_empty

from .foundation_errors import DiscoveryCancelledError


@dataclass(slots=True)
class CancellationToken:
    """Mutable cooperative token shared across one Discovery execution."""

    id: CanonicalId
    _cancelled: bool = field(default=False, init=False, repr=False)
    _reason: str | None = field(default=None, init=False, repr=False)
    _logger: logging.Logger = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Validate identity and initialize structured logging."""
        if not isinstance(self.id, CanonicalId):
            raise TypeError("id must be CanonicalId")
        self._logger = get_logger("core.discovery.cancellation")

    @classmethod
    def create(cls) -> "CancellationToken":
        """Create a token with a canonical identity and active state."""
        return cls(id=CanonicalId.new())

    @property
    def is_cancelled(self) -> bool:
        """Return whether cancellation was requested."""
        return self._cancelled

    @property
    def reason(self) -> str | None:
        """Return the normalized cancellation reason, when available."""
        return self._reason

    def cancel(self, reason: str = "cancellation requested") -> bool:
        """Request cancellation idempotently and return whether state changed."""
        normalized = require_non_empty(reason, "reason")
        if self._cancelled:
            return False
        self._cancelled = True
        self._reason = normalized
        self._logger.info(
            "discovery cancellation requested",
            extra={"context": {"token_id": str(self.id), "reason": normalized}},
        )
        return True

    def throw_if_cancelled(self) -> None:
        """Raise the canonical cancellation error when cancellation is active."""
        if self._cancelled:
            raise DiscoveryCancelledError(
                self._reason or "discovery execution was cancelled"
            )


__all__ = ["CancellationToken"]
