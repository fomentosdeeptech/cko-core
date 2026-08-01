"""Public API for the canonical CKO logical execution engine."""

from .engine import ExecutionEngine
from .errors import (
    ExecutionEngineError,
    ExecutionEngineValidationError,
    ExecutionOperatorError,
    ExecutionPipelineError,
    InvalidExecutionEngineModelError,
)
from .models import (
    ENGINE_SCHEMA_VERSION,
    EXECUTION_ENGINE_VERSION,
    ExecutionContext,
    ExecutionMetrics,
    ExecutionResult,
    ExecutionState,
    deterministic_execution_id,
)
from .operators import (
    CompositeIndexScanOperator,
    ExecutionOperator,
    FilterOperator,
    IndexScanOperator,
    LimitOperator,
    OperatorResult,
    OrderedScanOperator,
    PrefixScanOperator,
    ProjectionOperator,
    RootOperator,
    ScanOperator,
    SortOperator,
    canonical_operators,
)
from .pipeline import ExecutionPipeline, PipelineResult
from .validator import ExecutionEngineValidator, ExecutionValidator

__all__ = [
    "ENGINE_SCHEMA_VERSION", "EXECUTION_ENGINE_VERSION",
    "CompositeIndexScanOperator", "ExecutionContext", "ExecutionEngine",
    "ExecutionEngineError", "ExecutionEngineValidationError",
    "ExecutionEngineValidator", "ExecutionMetrics", "ExecutionOperator",
    "ExecutionOperatorError", "ExecutionPipeline", "ExecutionPipelineError",
    "ExecutionResult", "ExecutionState", "ExecutionValidator",
    "FilterOperator", "IndexScanOperator", "InvalidExecutionEngineModelError",
    "LimitOperator", "OperatorResult", "OrderedScanOperator",
    "PipelineResult", "PrefixScanOperator", "ProjectionOperator",
    "RootOperator", "ScanOperator", "SortOperator", "canonical_operators",
    "deterministic_execution_id",
]
