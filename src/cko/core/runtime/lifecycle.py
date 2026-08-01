"""Canonical lifecycle transitions for synchronous Runtime coordination."""

from __future__ import annotations

from .errors import RuntimeLifecycleError
from .models import RuntimeState


class LifecycleController:
    """Validate and apply the canonical Runtime state machine."""

    _transitions = {
        RuntimeState.CREATED: frozenset({
            RuntimeState.INITIALIZED, RuntimeState.FAILED, RuntimeState.CANCELLED,
        }),
        RuntimeState.INITIALIZED: frozenset({
            RuntimeState.READY, RuntimeState.FAILED, RuntimeState.CANCELLED,
        }),
        RuntimeState.READY: frozenset({
            RuntimeState.RUNNING, RuntimeState.FAILED, RuntimeState.CANCELLED,
        }),
        RuntimeState.RUNNING: frozenset({
            RuntimeState.PAUSED, RuntimeState.COMPLETED, RuntimeState.FAILED,
            RuntimeState.CANCELLED,
        }),
        RuntimeState.PAUSED: frozenset({
            RuntimeState.RUNNING, RuntimeState.FAILED, RuntimeState.CANCELLED,
        }),
        RuntimeState.COMPLETED: frozenset(),
        RuntimeState.FAILED: frozenset(),
        RuntimeState.CANCELLED: frozenset(),
    }

    def can_transition(
        self, current: RuntimeState, target: RuntimeState,
    ) -> bool:
        """Return whether a transition belongs to the canonical state graph."""
        source = self._state(current, "current")
        destination = self._state(target, "target")
        return destination in self._transitions[source]

    def validate_transition(
        self, current: RuntimeState, target: RuntimeState,
    ) -> None:
        """Raise when a transition is outside the canonical state graph."""
        source = self._state(current, "current")
        destination = self._state(target, "target")
        if destination not in self._transitions[source]:
            raise RuntimeLifecycleError(
                f"invalid runtime transition: {source.value} -> {destination.value}"
            )

    def transition(self, context: object, target: RuntimeState) -> RuntimeState:
        """Validate a context transition, apply it, and return the new state."""
        from .models import RuntimeContext

        if not isinstance(context, RuntimeContext):
            raise RuntimeLifecycleError("context must be RuntimeContext")
        destination = self._state(target, "target")
        self.validate_transition(context.state, destination)
        context.state = destination
        return destination

    @classmethod
    def allowed_transitions(cls, state: RuntimeState) -> frozenset[RuntimeState]:
        """Return the immutable set of transitions allowed from one state."""
        source = cls._state(state, "state")
        return cls._transitions[source]

    @staticmethod
    def _state(value: RuntimeState, name: str) -> RuntimeState:
        try:
            return RuntimeState(value)
        except (TypeError, ValueError) as error:
            raise RuntimeLifecycleError(f"{name} must be RuntimeState") from error


__all__ = ["LifecycleController"]
