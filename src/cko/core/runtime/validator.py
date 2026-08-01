"""Integrity validation for Runtime contexts, sessions, and transitions."""

from __future__ import annotations

from .errors import RuntimeLifecycleError, RuntimeValidationError
from .lifecycle import LifecycleController
from .models import RuntimeContext, RuntimeMetrics, RuntimeSession, RuntimeState
from .resources import ResourceRegistry


class RuntimeValidator:
    """Validate every public component of the canonical Runtime foundation."""

    def __init__(self, lifecycle: LifecycleController | None = None) -> None:
        self._lifecycle = lifecycle or LifecycleController()
        if not isinstance(self._lifecycle, LifecycleController):
            raise RuntimeValidationError("lifecycle must be LifecycleController")

    def validate_context(self, context: RuntimeContext) -> RuntimeContext:
        """Validate Runtime context identity, state, and mappings."""
        if not isinstance(context, RuntimeContext):
            raise RuntimeValidationError("context must be RuntimeContext")
        if context.state is not RuntimeState.CREATED and context.execution_id is None:
            raise RuntimeValidationError(
                "execution_id is required after Runtime creation"
            )
        return context

    def validate_session(self, session: RuntimeSession) -> RuntimeSession:
        """Validate the binding and metrics of a Runtime session."""
        if not isinstance(session, RuntimeSession):
            raise RuntimeValidationError("session must be RuntimeSession")
        self.validate_context(session.context)
        if not isinstance(session.metrics, RuntimeMetrics):
            raise RuntimeValidationError("session metrics must be RuntimeMetrics")
        if session.runtime != session.context.runtime_id:
            raise RuntimeValidationError("session Runtime identity is inconsistent")
        return session

    def validate_state(self, state: RuntimeState) -> RuntimeState:
        """Validate and normalize one canonical Runtime state."""
        try:
            return RuntimeState(state)
        except (TypeError, ValueError) as error:
            raise RuntimeValidationError("state must be RuntimeState") from error

    def validate_transition(
        self, current: RuntimeState, target: RuntimeState,
    ) -> None:
        """Validate one lifecycle transition through the canonical controller."""
        try:
            self._lifecycle.validate_transition(current, target)
        except RuntimeLifecycleError as error:
            raise RuntimeValidationError(str(error)) from error

    def validate_integrity(
        self, context: RuntimeContext, session: RuntimeSession,
        resources: ResourceRegistry,
    ) -> None:
        """Validate cross-model Runtime identity, metrics, and resources."""
        self.validate_context(context)
        self.validate_session(session)
        if session.context.to_dict() != context.to_dict():
            raise RuntimeValidationError("session does not match Runtime context")
        if not isinstance(resources, ResourceRegistry):
            raise RuntimeValidationError("resources must be ResourceRegistry")
        if dict(context.resources) != dict(resources.snapshot()):
            raise RuntimeValidationError("resource registry and context differ")
        if context.statistics != session.metrics.to_dict():
            raise RuntimeValidationError("context statistics and session metrics differ")

    def is_valid(
        self, context: RuntimeContext, session: RuntimeSession,
        resources: ResourceRegistry,
    ) -> bool:
        """Return whether complete Runtime integrity is valid."""
        try:
            self.validate_integrity(context, session, resources)
        except RuntimeValidationError:
            return False
        return True


__all__ = ["RuntimeValidator"]
