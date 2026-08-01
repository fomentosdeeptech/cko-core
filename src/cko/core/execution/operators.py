"""Canonical logical operator contracts without infrastructure access."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import ClassVar, Mapping

from cko.core.discovery.execution_models import ExecutionNode, ExecutionNodeType

from .errors import ExecutionOperatorError
from .models import ExecutionContext


def _freeze_metadata(value: Mapping[str, object]) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ExecutionOperatorError("operator metadata must be a mapping")
    normalized: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            raise ExecutionOperatorError(
                "operator metadata keys must be non-empty strings"
            )
        if item is not None and not isinstance(item, (bool, int, float, str)):
            raise ExecutionOperatorError(
                "operator metadata values must be scalar"
            )
        normalized[key.strip()] = item
    return MappingProxyType(dict(sorted(normalized.items())))


@dataclass(frozen=True, slots=True)
class OperatorResult:
    """Infrastructure-neutral outcome returned by an execution operator."""

    skipped: bool = False
    warnings: tuple[str, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.skipped, bool):
            raise ExecutionOperatorError("skipped must be boolean")
        warnings = tuple(self.warnings)
        if any(not isinstance(item, str) or not item.strip()
               for item in warnings):
            raise ExecutionOperatorError(
                "operator warnings must be non-empty strings"
            )
        object.__setattr__(self, "warnings", tuple(
            item.strip() for item in warnings
        ))
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))


class ExecutionOperator(ABC):
    """Abstract contract shared by every canonical execution operator."""

    node_type: ClassVar[ExecutionNodeType]

    def supports(self, node: ExecutionNode) -> bool:
        """Return whether this operator owns the supplied node type."""
        return isinstance(node, ExecutionNode) and node.node_type is self.node_type

    @abstractmethod
    def execute(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        """Execute only the logical contract represented by a physical node."""

    def _logical_result(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        if not isinstance(context, ExecutionContext):
            raise ExecutionOperatorError("context must be ExecutionContext")
        if not self.supports(node):
            raise ExecutionOperatorError(
                f"{type(self).__name__} does not support {node.node_type.value}"
            )
        return OperatorResult(metadata={"node_type": node.node_type.value})


class ScanOperator(ExecutionOperator):
    """Logical contract for full scans; performs no infrastructure access."""

    node_type = ExecutionNodeType.SCAN

    def execute(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        """Acknowledge a full-scan node without reading a data source."""
        return self._logical_result(node, context)


class FilterOperator(ExecutionOperator):
    """Logical contract for filter nodes."""

    node_type = ExecutionNodeType.FILTER

    def execute(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        """Acknowledge a filter node without evaluating business rules."""
        return self._logical_result(node, context)


class ProjectionOperator(ExecutionOperator):
    """Logical contract for projection nodes."""

    node_type = ExecutionNodeType.PROJECTION

    def execute(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        """Acknowledge a projection node without materializing records."""
        return self._logical_result(node, context)


class SortOperator(ExecutionOperator):
    """Logical contract for sort nodes."""

    node_type = ExecutionNodeType.SORT

    def execute(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        """Acknowledge a sort node without materializing records."""
        return self._logical_result(node, context)


class LimitOperator(ExecutionOperator):
    """Logical contract for limit nodes."""

    node_type = ExecutionNodeType.LIMIT

    def execute(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        """Acknowledge a limit node without materializing records."""
        return self._logical_result(node, context)


class IndexScanOperator(ExecutionOperator):
    """Logical contract for a single-index scan."""

    node_type = ExecutionNodeType.INDEX_SCAN

    def execute(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        """Acknowledge an index scan without accessing an index."""
        return self._logical_result(node, context)


class CompositeIndexScanOperator(ExecutionOperator):
    """Logical contract for a composite-index scan."""

    node_type = ExecutionNodeType.COMPOSITE_INDEX_SCAN

    def execute(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        """Acknowledge a composite scan without accessing an index."""
        return self._logical_result(node, context)


class PrefixScanOperator(ExecutionOperator):
    """Logical contract for a prefix-index scan."""

    node_type = ExecutionNodeType.PREFIX_SCAN

    def execute(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        """Acknowledge a prefix scan without accessing an index."""
        return self._logical_result(node, context)


class OrderedScanOperator(ExecutionOperator):
    """Logical contract for an ordered-index scan."""

    node_type = ExecutionNodeType.ORDERED_SCAN

    def execute(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        """Acknowledge an ordered scan without accessing an index."""
        return self._logical_result(node, context)


class RootOperator(ExecutionOperator):
    """Logical contract for the unique physical-plan root."""

    node_type = ExecutionNodeType.ROOT

    def execute(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        """Acknowledge the root boundary of a logical execution."""
        return self._logical_result(node, context)


def canonical_operators() -> Mapping[ExecutionNodeType, ExecutionOperator]:
    """Create the complete immutable registry of canonical operators."""
    operators: tuple[ExecutionOperator, ...] = (
        ScanOperator(), FilterOperator(), ProjectionOperator(), SortOperator(),
        LimitOperator(), IndexScanOperator(), CompositeIndexScanOperator(),
        PrefixScanOperator(), OrderedScanOperator(), RootOperator(),
    )
    return MappingProxyType({item.node_type: item for item in operators})


__all__ = [
    "CompositeIndexScanOperator", "ExecutionOperator", "FilterOperator",
    "IndexScanOperator", "LimitOperator", "OperatorResult",
    "OrderedScanOperator", "PrefixScanOperator", "ProjectionOperator",
    "RootOperator", "ScanOperator", "SortOperator", "canonical_operators",
]
