"""Cooperative cancellation without threads, async, or external resources."""

from __future__ import annotations

from dataclasses import dataclass, field

from .errors import InvalidRuntimeModelError, RuntimeCancellationError


def _reason(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidRuntimeModelError("cancellation reason must be non-empty")
    return value.strip()


@dataclass(slots=True)
class CancellationToken:
    """Mutable, idempotent token for cooperative Runtime cancellation."""

    _cancelled: bool = field(default=False, init=False, repr=False)
    _reason: str | None = field(default=None, init=False, repr=False)

    @property
    def is_cancelled(self) -> bool:
        """Return whether cancellation has been requested."""
        return self._cancelled

    @property
    def reason(self) -> str | None:
        """Return the normalized cancellation reason when present."""
        return self._reason

    def cancel(self, reason: str = "cancellation requested") -> bool:
        """Request cancellation idempotently and report whether state changed."""
        normalized = _reason(reason)
        if self._cancelled:
            return False
        self._cancelled = True
        self._reason = normalized
        return True

    def throw_if_cancelled(self) -> None:
        """Raise the canonical error when cancellation has been requested."""
        if self._cancelled:
            raise RuntimeCancellationError(
                self._reason or "runtime execution was cancelled"
            )

    def to_dict(self) -> dict[str, object]:
        """Serialize token state to primitive values."""
        return {"cancelled": self.is_cancelled, "reason": self.reason}


__all__ = ["CancellationToken"]
