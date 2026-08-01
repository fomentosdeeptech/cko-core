"""Canonical deterministic execution engine for immutable physical plans."""

from __future__ import annotations

from typing import Mapping

from cko.core.discovery.execution_models import ExecutionNodeType, ExecutionPlan
from cko.core.logging import get_logger

from .errors import ExecutionEngineError
from .models import (
    EXECUTION_ENGINE_VERSION,
    ExecutionContext,
    ExecutionMetrics,
    ExecutionResult,
    ExecutionState,
)
from .operators import ExecutionOperator
from .pipeline import ExecutionPipeline, PipelineResult
from .validator import ExecutionEngineValidator


def _event(logger: object, name: str, **context: object) -> None:
    method = "error" if name == "execution_failed" else "info"
    getattr(logger, method)(
        name,
        extra={
            "event": f"core.execution.engine.{name}",
            "context": dict(sorted(context.items())),
        },
    )


class ExecutionEngine:
    """Validate, traverse, and logically execute a physical plan."""

    def __init__(
        self,
        operators: Mapping[ExecutionNodeType, ExecutionOperator] | None = None,
        *,
        validator: ExecutionEngineValidator | None = None,
    ) -> None:
        self._pipeline = ExecutionPipeline(operators)
        self._validator = validator or ExecutionEngineValidator()
        if not isinstance(self._validator, ExecutionEngineValidator):
            raise ExecutionEngineError(
                "validator must be ExecutionEngineValidator"
            )
        self._logger = get_logger("core.execution.engine")

    @property
    def pipeline(self) -> ExecutionPipeline:
        """Return the deterministic pipeline owned by this engine."""
        return self._pipeline

    def execute(
        self,
        plan: ExecutionPlan,
        *,
        metadata: Mapping[str, object] | None = None,
    ) -> ExecutionResult:
        """Execute a validated physical plan and return an immutable result."""
        context: ExecutionContext | None = None
        try:
            context = ExecutionContext(
                execution_plan=plan,
                metadata={} if metadata is None else metadata,
                statistics={"duration_unit": "logical"},
            )
            _event(
                self._logger, "execution_started",
                execution_id=context.execution_id,
                plan_id=getattr(plan, "plan_id", None),
            )
            self._validator.validate_context(
                context, self._pipeline.operators
            )
            context.transition_to(ExecutionState.READY)
            context.transition_to(ExecutionState.RUNNING)
            pipeline_result = self._pipeline.execute(context)
            context.transition_to(ExecutionState.COMPLETED)
            result = self._result(context, pipeline_result, success=True)
            _event(
                self._logger, "execution_finished",
                execution_id=context.execution_id,
                executed_nodes=len(result.executed_nodes),
                skipped_nodes=len(result.skipped_nodes),
                success=True,
            )
            return result
        except Exception as error:
            if context is not None and context.state in {
                ExecutionState.CREATED, ExecutionState.READY,
                ExecutionState.RUNNING,
            }:
                context.transition_to(ExecutionState.FAILED)
            _event(
                self._logger, "execution_failed",
                error_type=type(error).__name__,
                execution_id=(
                    context.execution_id if context is not None else None
                ),
                plan_id=getattr(plan, "plan_id", None),
            )
            raise

    @staticmethod
    def _result(
        context: ExecutionContext,
        pipeline: PipelineResult,
        *,
        success: bool,
    ) -> ExecutionResult:
        metrics = ExecutionMetrics(
            duration=0.0,
            nodes_executed=len(pipeline.executed_nodes),
            maximum_depth=pipeline.maximum_depth,
            warnings=pipeline.warnings,
            metadata={
                "deterministic": True,
                "duration_kind": "logical",
                "engine_version": EXECUTION_ENGINE_VERSION,
            },
        )
        return ExecutionResult(
            execution_id=context.execution_id,
            success=success,
            executed_nodes=pipeline.executed_nodes,
            skipped_nodes=pipeline.skipped_nodes,
            warnings=pipeline.warnings,
            metadata={
                "context_metadata": context.metadata,
                "deterministic": True,
                "engine_version": EXECUTION_ENGINE_VERSION,
                "final_state": context.state.value,
                "plan_id": context.execution_plan.plan_id,
            },
            statistics=metrics,
        )


__all__ = ["ExecutionEngine"]
