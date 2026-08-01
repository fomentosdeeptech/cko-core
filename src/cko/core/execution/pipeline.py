"""Deterministic pre-order pipeline for canonical physical execution trees."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from cko.core.discovery.execution_models import ExecutionNode, ExecutionNodeType
from cko.core.logging import get_logger

from .errors import ExecutionOperatorError, ExecutionPipelineError
from .models import ExecutionContext, ExecutionState
from .operators import (
    ExecutionOperator,
    OperatorResult,
    canonical_operators,
)


def _event(logger: object, name: str, **context: object) -> None:
    getattr(logger, "info")(
        name,
        extra={
            "event": f"core.execution.engine.{name}",
            "context": dict(sorted(context.items())),
        },
    )


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Ordered logical outcomes produced by a pre-order traversal."""

    executed_nodes: tuple[str, ...]
    skipped_nodes: tuple[str, ...]
    warnings: tuple[str, ...]
    maximum_depth: int


class ExecutionPipeline:
    """Visit and execute a physical tree in deterministic pre-order."""

    def __init__(
        self,
        operators: Mapping[ExecutionNodeType, ExecutionOperator] | None = None,
    ) -> None:
        selected = canonical_operators() if operators is None else operators
        if not isinstance(selected, Mapping):
            raise ExecutionPipelineError("operators must be a mapping")
        self._operators = MappingProxyType(dict(selected))
        self._logger = get_logger("core.execution.engine")

    @property
    def operators(self) -> Mapping[ExecutionNodeType, ExecutionOperator]:
        """Expose the immutable operator registry used by this pipeline."""
        return self._operators

    def execute(self, context: ExecutionContext) -> PipelineResult:
        """Execute every physical node once in deterministic pre-order."""
        if not isinstance(context, ExecutionContext):
            raise ExecutionPipelineError("context must be ExecutionContext")
        if context.state is not ExecutionState.RUNNING:
            raise ExecutionPipelineError("context must be in RUNNING state")
        executed: list[str] = []
        skipped: list[str] = []
        warnings: list[str] = []
        active: set[int] = set()
        visited: set[int] = set()
        maximum_depth = 0

        def visit(node: ExecutionNode, depth: int) -> None:
            """Visit one node and then each child in canonical tuple order."""
            nonlocal maximum_depth
            identity = id(node)
            if identity in active:
                raise ExecutionPipelineError("execution tree contains a cycle")
            if identity in visited:
                raise ExecutionPipelineError(
                    "execution tree reuses a node object"
                )
            operator = self._operators.get(node.node_type)
            if operator is None or not isinstance(operator, ExecutionOperator):
                raise ExecutionPipelineError(
                    f"operator is missing for {node.node_type.value}"
                )
            active.add(identity)
            visited.add(identity)
            maximum_depth = max(maximum_depth, depth)
            context.push(node.node_id)
            _event(
                self._logger, "node_execution_started",
                execution_id=context.execution_id,
                node_id=node.node_id,
                node_type=node.node_type.value,
            )
            try:
                outcome = operator.execute(node, context)
                if not isinstance(outcome, OperatorResult):
                    raise ExecutionOperatorError(
                        "operator must return OperatorResult"
                    )
                destination = skipped if outcome.skipped else executed
                destination.append(node.node_id)
                warnings.extend(outcome.warnings)
                _event(
                    self._logger, "node_execution_finished",
                    execution_id=context.execution_id,
                    node_id=node.node_id,
                    node_type=node.node_type.value,
                    skipped=outcome.skipped,
                )
                for child in node.children:
                    visit(child, depth + 1)
            except ExecutionPipelineError:
                raise
            except Exception as error:
                raise ExecutionOperatorError(
                    f"operator failed for node {node.node_id}: {error}"
                ) from error
            finally:
                if context.execution_stack and (
                    context.execution_stack[-1] == node.node_id
                ):
                    context.pop()
                active.discard(identity)

        visit(context.execution_plan.root_node, 1)
        return PipelineResult(
            executed_nodes=tuple(executed),
            skipped_nodes=tuple(skipped),
            warnings=tuple(warnings),
            maximum_depth=maximum_depth,
        )


__all__ = ["ExecutionPipeline", "PipelineResult"]
