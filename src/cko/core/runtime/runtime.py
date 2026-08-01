"""Canonical synchronous Runtime coordinating execution lifecycle and resources."""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Mapping

from cko.core.discovery.execution_models import ExecutionPlan
from cko.core.execution import ExecutionEngine, ExecutionResult
from cko.core.execution.models import deterministic_execution_id
from cko.core.logging import get_logger

from .cancellation import CancellationToken
from .errors import RuntimeCancellationError, RuntimeErrorBase
from .lifecycle import LifecycleController
from .models import (
    RUNTIME_VERSION,
    RuntimeContext,
    RuntimeMetrics,
    RuntimeReport,
    RuntimeSession,
    RuntimeState,
)
from .resources import ResourceRegistry
from .validator import RuntimeValidator


def _identifier(value: str | None, prefix: str) -> str:
    if value is None:
        return f"{prefix}-{uuid.uuid4()}"
    if not isinstance(value, str) or not value.strip():
        raise RuntimeErrorBase(f"{prefix}_id must be a non-empty string")
    return value.strip()


def _event(logger: object, name: str, **context: object) -> None:
    getattr(logger, "info")(
        name,
        extra={
            "event": f"core.runtime.{name}",
            "context": dict(sorted(context.items())),
        },
    )


class Runtime:
    """Coordinate one Execution Engine lifecycle without executing operators."""

    def __init__(
        self,
        engine: ExecutionEngine | None = None,
        *,
        runtime_id: str | None = None,
        session_id: str | None = None,
        metadata: Mapping[str, object] | None = None,
        validator: RuntimeValidator | None = None,
    ) -> None:
        self._engine = engine or ExecutionEngine()
        if not isinstance(self._engine, ExecutionEngine):
            raise RuntimeErrorBase("engine must be ExecutionEngine")
        self._lifecycle = LifecycleController()
        self._validator = validator or RuntimeValidator(self._lifecycle)
        if not isinstance(self._validator, RuntimeValidator):
            raise RuntimeErrorBase("validator must be RuntimeValidator")
        self._resources = ResourceRegistry()
        self._cancellation = CancellationToken()
        self._runtime_id = _identifier(runtime_id, "runtime")
        self._session_id = _identifier(session_id, "session")
        self._context = RuntimeContext(
            runtime_id=self._runtime_id,
            execution_id=f"execution-{self._runtime_id}",
            metadata={} if metadata is None else metadata,
        )
        self._plan: ExecutionPlan | None = None
        self._result: ExecutionResult | None = None
        self._created_at = time.perf_counter()
        self._finished_at: float | None = None
        self._executions = 0
        self._cancelled = 0
        self._failed = 0
        self._completed = 0
        self._logger = get_logger("core.runtime")
        self._sync_context()
        _event(self._logger, "runtime_created", runtime_id=self.runtime_id)

    @property
    def runtime_id(self) -> str:
        """Return the canonical Runtime identity."""
        return self._runtime_id

    @property
    def context(self) -> RuntimeContext:
        """Return the live Runtime context."""
        return self._context

    @property
    def state(self) -> RuntimeState:
        """Return the current Runtime state."""
        return self._context.state

    @property
    def metrics(self) -> RuntimeMetrics:
        """Return an immutable metrics snapshot."""
        endpoint = self._finished_at or time.perf_counter()
        return RuntimeMetrics(
            runtime_duration=max(0.0, endpoint - self._created_at),
            executions=self._executions,
            cancelled=self._cancelled,
            failed=self._failed,
            completed=self._completed,
            metadata={"runtime_version": RUNTIME_VERSION, "synchronous": True},
        )

    @property
    def resources(self) -> ResourceRegistry:
        """Return the logical resource registry owned by this Runtime."""
        return self._resources

    @property
    def cancellation_token(self) -> CancellationToken:
        """Return the cooperative cancellation token."""
        return self._cancellation

    @property
    def result(self) -> ExecutionResult | None:
        """Return the Execution Engine result when execution completed."""
        return self._result

    @property
    def session(self) -> RuntimeSession:
        """Return an immutable view of the current Runtime session."""
        metrics = self.metrics
        self._context.resources = self.resources.snapshot()
        self._context.statistics = metrics.to_dict()
        context = RuntimeContext.from_dict(self.context.to_dict())
        return RuntimeSession(
            session_id=self._session_id,
            runtime=self.runtime_id,
            context=context,
            metrics=metrics,
            metadata={"runtime_version": RUNTIME_VERSION},
        )

    def initialize(self, plan: ExecutionPlan) -> RuntimeContext:
        """Bind an ExecutionPlan and initialize the Runtime context."""
        if self.state is not RuntimeState.CREATED:
            raise RuntimeErrorBase("Runtime can only initialize from CREATED")
        execution_id = deterministic_execution_id(plan)
        self._plan = plan
        self._context.execution_id = execution_id
        self._lifecycle.transition(self.context, RuntimeState.INITIALIZED)
        self._sync_context()
        self._validator.validate_context(self.context)
        _event(
            self._logger, "runtime_initialized",
            execution_id=execution_id, runtime_id=self.runtime_id,
        )
        return self.context

    def ready(self) -> RuntimeContext:
        """Move an initialized Runtime into the READY state."""
        self._lifecycle.transition(self.context, RuntimeState.READY)
        self._sync_context()
        return self.context

    def start(self, plan: ExecutionPlan | None = None) -> ExecutionResult:
        """Coordinate synchronous execution and return the Engine result."""
        if self.state is RuntimeState.CREATED:
            if plan is None:
                raise RuntimeErrorBase("plan is required to start a new Runtime")
            self.initialize(plan)
        elif plan is not None and plan is not self._plan:
            raise RuntimeErrorBase("Runtime is already bound to another plan")
        if self.state is RuntimeState.INITIALIZED:
            self.ready()
        if self.state is not RuntimeState.READY or self._plan is None:
            raise RuntimeErrorBase("Runtime must be READY before start")
        if self.cancellation_token.is_cancelled:
            self.cancel(self.cancellation_token.reason or "cancellation requested")
            self.cancellation_token.throw_if_cancelled()
        self._lifecycle.transition(self.context, RuntimeState.RUNNING)
        self._executions += 1
        self._sync_context()
        _event(
            self._logger, "runtime_started",
            execution_id=self.context.execution_id, runtime_id=self.runtime_id,
        )
        try:
            result = self._engine.execute(
                self._plan, metadata=self.context.metadata
            )
        except Exception:
            self._lifecycle.transition(self.context, RuntimeState.FAILED)
            self._failed += 1
            self._finish_clock()
            self._sync_context()
            _event(
                self._logger, "runtime_finished",
                runtime_id=self.runtime_id, state=self.state.value, success=False,
            )
            raise
        self._result = result
        self.finish()
        return result

    def execute(self, plan: ExecutionPlan | None = None) -> ExecutionResult:
        """Alias for starting one synchronous Runtime execution."""
        return self.start(plan)

    def pause(self) -> RuntimeState:
        """Pause lifecycle coordination at a cooperative boundary."""
        return self._lifecycle.transition(self.context, RuntimeState.PAUSED)

    def resume(self) -> RuntimeState:
        """Resume lifecycle coordination from a cooperative pause."""
        return self._lifecycle.transition(self.context, RuntimeState.RUNNING)

    def finish(self) -> RuntimeReport:
        """Finalize a running Runtime and return its terminal report."""
        if self.state is RuntimeState.PAUSED:
            self.resume()
        self._lifecycle.transition(self.context, RuntimeState.COMPLETED)
        self._completed += 1
        self._finish_clock()
        self._sync_context()
        _event(
            self._logger, "runtime_finished",
            runtime_id=self.runtime_id, state=self.state.value, success=True,
        )
        return self.report()

    def cancel(self, reason: str = "cancellation requested") -> bool:
        """Cooperatively cancel an active Runtime without concurrency."""
        if self.state in {
            RuntimeState.COMPLETED, RuntimeState.FAILED, RuntimeState.CANCELLED,
        }:
            return False
        changed = self.cancellation_token.cancel(reason)
        self._lifecycle.transition(self.context, RuntimeState.CANCELLED)
        if self._executions == 0:
            self._executions = 1
        self._cancelled += 1
        self._finish_clock()
        self._sync_context()
        _event(
            self._logger, "runtime_cancelled",
            reason=self.cancellation_token.reason, runtime_id=self.runtime_id,
        )
        return changed

    def register_resource(self, name: str, value: object = None) -> None:
        """Register a logical resource and synchronize the context snapshot."""
        self.resources.register(name, value)
        self._sync_context()

    def unregister_resource(self, name: str) -> object:
        """Unregister a logical resource and synchronize the context snapshot."""
        value = self.resources.unregister(name)
        self._sync_context()
        return value

    def release_resources(self) -> None:
        """Release all logical resource registrations."""
        self.resources.clear()
        self._sync_context()

    def report(self) -> RuntimeReport:
        """Build and validate a timestamped Runtime report."""
        session = self.session
        self._validator.validate_integrity(self.context, session, self.resources)
        return RuntimeReport(
            session=session,
            state=self.state,
            metrics=session.metrics,
            timestamp=datetime.now(timezone.utc),
        )

    def _finish_clock(self) -> None:
        self._finished_at = time.perf_counter()

    def _sync_context(self) -> None:
        self._context.resources = self.resources.snapshot()
        self._context.statistics = self.metrics.to_dict()


__all__ = ["Runtime"]
