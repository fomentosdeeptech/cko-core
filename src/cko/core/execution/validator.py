"""Validation for plans, engine contexts, states, and operator registries."""

from __future__ import annotations

from typing import Mapping

from cko.core.discovery.execution_models import (
    ExecutionNode,
    ExecutionNodeType,
    ExecutionPlan,
)
from cko.core.discovery.execution_planner import ExecutionPlanValidator

from .errors import ExecutionEngineValidationError
from .models import ExecutionContext, ExecutionState
from .operators import ExecutionOperator, canonical_operators


class ExecutionEngineValidator:
    """Validate all inputs required by deterministic logical execution."""

    def validate(
        self,
        plan: ExecutionPlan,
        operators: Mapping[ExecutionNodeType, ExecutionOperator] | None = None,
    ) -> ExecutionPlan:
        """Return a valid physical plan or raise a precise engine error."""
        try:
            ExecutionPlanValidator().validate(plan)
        except (ValueError, TypeError, KeyError) as error:
            raise ExecutionEngineValidationError(
                f"invalid execution plan: {error}"
            ) from error
        registry = canonical_operators() if operators is None else operators
        self.validate_operators(registry)
        self._validate_tree(plan.root_node, registry)
        if not isinstance(plan.metadata, Mapping):
            raise ExecutionEngineValidationError(
                "execution plan metadata must be a mapping"
            )
        if any(not isinstance(key, str) or not key.strip()
               for key in plan.metadata):
            raise ExecutionEngineValidationError(
                "execution plan metadata keys are invalid"
            )
        return plan

    def validate_context(
        self,
        context: ExecutionContext,
        operators: Mapping[ExecutionNodeType, ExecutionOperator] | None = None,
    ) -> ExecutionContext:
        """Validate context state, stack, metadata, statistics, and plan."""
        if not isinstance(context, ExecutionContext):
            raise ExecutionEngineValidationError(
                "context must be ExecutionContext"
            )
        if not isinstance(context.state, ExecutionState):
            raise ExecutionEngineValidationError("context state is invalid")
        if context.state is not ExecutionState.CREATED:
            raise ExecutionEngineValidationError(
                "new execution context must be in CREATED state"
            )
        if context.execution_stack:
            raise ExecutionEngineValidationError(
                "new execution context stack must be empty"
            )
        if not isinstance(context.metadata, Mapping):
            raise ExecutionEngineValidationError("context metadata is invalid")
        if not isinstance(context.statistics, Mapping):
            raise ExecutionEngineValidationError("context statistics are invalid")
        self.validate(context.execution_plan, operators)
        return context

    def validate_operators(
        self, operators: Mapping[ExecutionNodeType, ExecutionOperator],
    ) -> Mapping[ExecutionNodeType, ExecutionOperator]:
        """Validate registry key integrity and canonical operator ownership."""
        if not isinstance(operators, Mapping):
            raise ExecutionEngineValidationError(
                "operators must be a mapping"
            )
        for key, operator in operators.items():
            if not isinstance(key, ExecutionNodeType):
                raise ExecutionEngineValidationError(
                    "operator keys must be ExecutionNodeType"
                )
            if not isinstance(operator, ExecutionOperator):
                raise ExecutionEngineValidationError(
                    "operator registry contains an invalid operator"
                )
            if operator.node_type is not key:
                raise ExecutionEngineValidationError(
                    "operator registry key does not match operator type"
                )
        return operators

    def is_valid(
        self,
        plan: object,
        operators: Mapping[ExecutionNodeType, ExecutionOperator] | None = None,
    ) -> bool:
        """Return whether an object is executable by the engine."""
        try:
            self.validate(plan, operators)  # type: ignore[arg-type]
        except (ExecutionEngineValidationError, ValueError, TypeError, KeyError):
            return False
        return True

    @staticmethod
    def _validate_tree(
        root: ExecutionNode,
        operators: Mapping[ExecutionNodeType, ExecutionOperator],
    ) -> None:
        active: set[int] = set()
        visited: set[int] = set()

        def visit(node: ExecutionNode) -> None:
            """Validate one node and recursively validate its descendants."""
            identity = id(node)
            if identity in active:
                raise ExecutionEngineValidationError(
                    "execution tree contains a cycle"
                )
            if identity in visited:
                raise ExecutionEngineValidationError(
                    "execution tree reuses a node object"
                )
            operator = operators.get(node.node_type)
            if operator is None or not operator.supports(node):
                raise ExecutionEngineValidationError(
                    f"operator is missing for {node.node_type.value}"
                )
            active.add(identity)
            visited.add(identity)
            for child in node.children:
                visit(child)
            active.remove(identity)

        visit(root)


ExecutionValidator = ExecutionEngineValidator


__all__ = ["ExecutionEngineValidator", "ExecutionValidator"]
