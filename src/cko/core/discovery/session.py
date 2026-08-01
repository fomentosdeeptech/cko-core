"""Canonical state and metrics for a complete Discovery session."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import Enum

from cko.core.identity import CanonicalId
from cko.core.logging import get_logger
from cko.core.utils import ensure_aware, require_non_empty

from .foundation_errors import DiscoverySessionStateError
from .models import DiscoveryContext, DiscoveryRequest, DiscoveryResult
from .streaming_models import StreamMetrics


class DiscoverySessionState(str, Enum):
    """Lifecycle states accepted by a Discovery session."""

    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class DiscoverySessionMetrics:
    """Execution metrics accumulated by the session orchestration layer."""

    started_at: datetime | None = None
    completed_at: datetime | None = None
    observed_count: int = 0
    accepted_count: int = 0
    rejected_count: int = 0
    warning_count: int = 0
    error_count: int = 0

    def __post_init__(self) -> None:
        """Normalize timestamps and reject inconsistent counters."""
        if self.started_at is not None:
            object.__setattr__(self, "started_at", ensure_aware(self.started_at))
        if self.completed_at is not None:
            completed_at = ensure_aware(self.completed_at)
            if self.started_at is None:
                raise ValueError("completed_at requires started_at")
            if completed_at < self.started_at:
                raise ValueError("completed_at cannot precede started_at")
            object.__setattr__(self, "completed_at", completed_at)
        for name in (
            "observed_count",
            "accepted_count",
            "rejected_count",
            "warning_count",
            "error_count",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} cannot be negative")


@dataclass(slots=True)
class DiscoverySession:
    """Stateful canonical session controlled only by valid transitions."""

    id: CanonicalId
    request: DiscoveryRequest
    context: DiscoveryContext
    state: DiscoverySessionState = DiscoverySessionState.CREATED
    metrics: DiscoverySessionMetrics = field(default_factory=DiscoverySessionMetrics)
    provider_id: str | None = None
    failure: str | None = None
    _logger: logging.Logger = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Validate session identity, request context and initial state."""
        if not isinstance(self.id, CanonicalId):
            raise TypeError("id must be CanonicalId")
        if not isinstance(self.request, DiscoveryRequest):
            raise TypeError("request must be DiscoveryRequest")
        if not isinstance(self.context, DiscoveryContext):
            raise TypeError("context must be DiscoveryContext")
        if self.context != self.request.context:
            raise ValueError("session context must match request context")
        self.state = DiscoverySessionState(self.state)
        self._logger = get_logger("core.discovery.session")

    @classmethod
    def create(cls, request: DiscoveryRequest) -> "DiscoverySession":
        """Create a canonical session for a validated request."""
        return cls(
            id=CanonicalId.new(),
            request=request,
            context=request.context,
        )

    def start(self, provider_id: str, started_at: datetime) -> None:
        """Move a newly created session to its running state."""
        self._require_state(DiscoverySessionState.CREATED)
        self.provider_id = require_non_empty(provider_id, "provider_id")
        self.metrics = replace(
            self.metrics,
            started_at=ensure_aware(started_at),
        )
        self.state = DiscoverySessionState.RUNNING
        self._log_transition()

    def complete(self, result: DiscoveryResult, completed_at: datetime) -> None:
        """Close the session from the canonical provider result status."""
        self._require_state(DiscoverySessionState.RUNNING)
        if result.request_id != self.request.id:
            raise ValueError("result request_id does not match the session")
        finished = ensure_aware(completed_at)
        self.metrics = DiscoverySessionMetrics(
            started_at=self.metrics.started_at,
            completed_at=finished,
            observed_count=result.metrics.observed_count,
            accepted_count=result.metrics.accepted_count,
            rejected_count=result.metrics.rejected_count,
            warning_count=result.metrics.warning_count,
            error_count=result.metrics.error_count,
        )
        if result.status.value == "cancelled":
            self.state = DiscoverySessionState.CANCELLED
            self.failure = "provider returned a cancelled result"
        elif result.status.value == "failed":
            self.state = DiscoverySessionState.FAILED
            self.failure = "provider returned a failed result"
        else:
            self.state = DiscoverySessionState.COMPLETED
        self._log_transition()

    def complete_stream(
        self,
        metrics: StreamMetrics,
        completed_at: datetime,
    ) -> None:
        """Complete a streaming session without aggregating a DiscoveryResult."""
        self._require_state(DiscoverySessionState.RUNNING)
        if not isinstance(metrics, StreamMetrics):
            raise TypeError("metrics must be StreamMetrics")
        if metrics.terminal_state is None or metrics.terminal_state.value != "completed":
            raise ValueError("stream metrics must represent successful completion")
        finished = ensure_aware(completed_at)
        self.metrics = DiscoverySessionMetrics(
            started_at=self.metrics.started_at,
            completed_at=finished,
            observed_count=metrics.items_produced,
            accepted_count=metrics.items_consumed,
            rejected_count=metrics.items_rejected,
            warning_count=0,
            error_count=0,
        )
        self.state = DiscoverySessionState.COMPLETED
        self._log_transition()

    def fail(self, message: str, completed_at: datetime) -> None:
        """Record a controlled terminal failure for a running session."""
        self._terminate(
            DiscoverySessionState.FAILED,
            require_non_empty(message, "message"),
            completed_at,
            error_count=self.metrics.error_count + 1,
        )

    def cancel(self, reason: str, completed_at: datetime) -> None:
        """Record cooperative cancellation for a created or running session."""
        self._terminate(
            DiscoverySessionState.CANCELLED,
            require_non_empty(reason, "reason"),
            completed_at,
            error_count=self.metrics.error_count,
        )

    def _terminate(
        self,
        target: DiscoverySessionState,
        message: str,
        completed_at: datetime,
        *,
        error_count: int,
    ) -> None:
        """Apply a failure or cancellation terminal transition."""
        if self.state not in {
            DiscoverySessionState.CREATED,
            DiscoverySessionState.RUNNING,
        }:
            raise DiscoverySessionStateError(
                f"cannot transition session from {self.state.value} to {target.value}"
            )
        finished = ensure_aware(completed_at)
        started_at = self.metrics.started_at or finished
        self.metrics = replace(
            self.metrics,
            started_at=started_at,
            completed_at=finished,
            error_count=error_count,
        )
        self.failure = message
        self.state = target
        self._log_transition()

    def _require_state(self, expected: DiscoverySessionState) -> None:
        """Require the current state before applying a transition."""
        if self.state is not expected:
            raise DiscoverySessionStateError(
                f"session must be {expected.value}, not {self.state.value}"
            )

    def _log_transition(self) -> None:
        """Emit a structured session transition record."""
        self._logger.info(
            "discovery session transitioned",
            extra={
                "context": {
                    "session_id": str(self.id),
                    "request_id": str(self.request.id),
                    "state": self.state.value,
                    "provider_id": self.provider_id,
                }
            },
        )


__all__ = [
    "DiscoverySession",
    "DiscoverySessionMetrics",
    "DiscoverySessionState",
]
