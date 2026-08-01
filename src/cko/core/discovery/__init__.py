"""Public API for the infrastructure-neutral CKO Discovery boundary."""

from .cancellation import CancellationToken
from .capability_errors import (
    CapabilityConflictError,
    CapabilityDependencyError,
    CapabilityError,
    CapabilityNegotiationError,
    CapabilityValidationError,
    InvalidCapabilityError,
)
from .capability_models import (
    CAPABILITY_SCHEMA_VERSION,
    Capability,
    CapabilityCategory,
    CapabilityReport,
    CapabilityRequirement,
    CapabilityRequirementType,
    CapabilitySet,
)
from .capability_negotiation import CapabilityNegotiationEngine
from .capability_validation import (
    CapabilityResolver,
    CapabilityValidationEngine,
)
from .checkpoints import DiscoveryCheckpoint
from .contracts import (
    DiscoveryAssetMapper,
    DiscoveryEventPublisher,
    DiscoveryProvider,
    DiscoverySource,
    DiscoveryValidator,
)
from .execution import (
    AsyncDiscoveryProvider,
    ContextualDiscoveryProvider,
    DiscoveryExecutionContext,
    DiscoveryExecutor,
)
from .foundation_errors import (
    DiscoveryCancelledError,
    DiscoveryExecutionError,
    DiscoveryProviderNotFoundError,
    DiscoveryProviderRegistrationError,
    DiscoveryProviderResolutionError,
    DiscoverySessionStateError,
)
from .errors import (
    DiscoveryError,
    DiscoveryMappingError,
    DiscoveryProviderError,
    DiscoveryValidationError,
    InvalidDiscoveredItemError,
    InvalidDiscoveryRequestError,
    InvalidDiscoverySourceError,
    UnsupportedDiscoveryCapabilityError,
)
from .events import (
    DISCOVERY_BATCH_COMPLETED,
    DISCOVERY_CANCELLED,
    DISCOVERY_COMPLETED,
    DISCOVERY_EVENT_NAMES,
    DISCOVERY_FAILED,
    DISCOVERY_ITEM_OBSERVED,
    DISCOVERY_ITEM_REJECTED,
    DISCOVERY_STARTED,
    create_discovery_event,
)
from .mapper import DefaultDiscoveryAssetMapper
from .identity_contracts import (
    CanonicalIdentityAllocator,
    IdentityCandidateProvider,
    IdentityEvidenceEvaluator,
)
from .identity_errors import (
    IdentityAllocationError,
    IdentityAmbiguityError,
    IdentityCandidateProviderError,
    IdentityConflictError,
    IdentityEvidenceEvaluationError,
    IdentityResolutionCancelledError,
    IdentityResolutionError,
    InvalidIdentityCandidateError,
    InvalidIdentityEvidenceError,
    InvalidIdentityPolicyError,
    InvalidIdentityResolutionRequestError,
)
from .identity_models import (
    IDENTITY_RESOLUTION_SCHEMA_VERSION,
    ConflictBehavior,
    ConflictSeverity,
    EvidenceEvaluation,
    IdentityCandidate,
    IdentityConflict,
    IdentityEvidence,
    IdentityEvidenceType,
    IdentityFingerprint,
    IdentityResolutionRequest,
    InsufficientEvidenceBehavior,
    ResolutionDecision,
    ResolutionPolicy,
    ResolutionStatus,
)
from .identity_resolution import (
    DefaultCanonicalIdentityAllocator,
    DefaultNeutralEvidenceEvaluator,
    IdentityResolutionEngine,
)
from .models import (
    DISCOVERY_SCHEMA_VERSION,
    DiscoveredItem,
    DiscoveryBatch,
    DiscoveryCapability,
    DiscoveryContext,
    DiscoveryErrorRecord,
    DiscoveryEvidence,
    DiscoveryMetrics,
    DiscoveryPolicy,
    DiscoveryRequest,
    DiscoveryResult,
    DiscoveryScope,
    DiscoverySourceId,
    DiscoveryStatus,
    DiscoveryWarning,
    discovery_model_from_dict,
)
from .policies import ensure_supported_capabilities, validate_policy
from .pipeline import DiscoveryExecution, DiscoveryPipeline
from .query_errors import (
    InvalidFilterError,
    InvalidOrderingError,
    InvalidPaginationError,
    InvalidProjectionError,
    InvalidQueryError,
    QueryError,
    QueryResolutionError,
    QueryValidationError,
)
from .query_models import (
    QUERY_SCHEMA_VERSION,
    DiscoveryQuery,
    FilterGroup,
    FilterGroupOperator,
    QueryFilter,
    QueryOperator,
    QueryOrdering,
    QueryOrderingDirection,
    QueryPagination,
    QueryPlan,
    QueryProjection,
)
from .query_resolution import QueryResolver
from .query_validation import QueryValidationEngine
from .query_evaluation_contracts import (
    AttributeResolver,
    AttributeValue,
    MappingQueryEvaluationSubject,
    QueryEvaluationStream,
    QueryEvaluationSubject,
)
from .query_evaluation_errors import (
    AttributeResolutionError,
    FilterGroupEvaluationError,
    InvalidQueryEvaluationPolicyError,
    InvalidQueryEvaluationSubjectError,
    PredicateEvaluationError,
    QueryEvaluationCancelledError,
    QueryEvaluationError,
    QueryEvaluationLimitError,
    QueryOrderingEvaluationError,
    QueryPaginationEvaluationError,
    QueryProjectionEvaluationError,
)
from .query_evaluation_models import (
    QUERY_EVALUATION_SCHEMA_VERSION,
    EvaluationErrorBehavior,
    IncompatibleTypeBehavior,
    MissingAttributeBehavior,
    OrderingValuePosition,
    PredicateEvaluationRecord,
    ProjectedQueryItem,
    QueryEvaluationContext,
    QueryEvaluationPolicy,
    QueryEvaluationResult,
    QueryMatchResult,
)
from .query_evaluation import (
    DefaultAttributeResolver,
    DefaultQueryEvaluationStream,
    FilterGroupEvaluator,
    QueryEvaluationEngine,
    QueryOrderingEngine,
    QueryPaginationEngine,
    QueryPredicateEvaluator,
    QueryProjectionEngine,
)
from .query_index import (
    LogicalIndexBuilder,
    LogicalIndexResolver,
    LogicalIndexValidator,
    QueryIndexPlanner,
)
from .query_index_errors import (
    InvalidLogicalIndexError,
    InvalidLogicalIndexPolicyError,
    LogicalIndexError,
    LogicalIndexResolutionError,
    LogicalIndexValidationError,
)
from .query_index_models import (
    QUERY_INDEX_SCHEMA_VERSION,
    DiscardedLogicalIndex,
    DuplicateBehavior,
    IndexStrategy,
    LogicalIndex,
    LogicalIndexEntry,
    LogicalIndexPolicy,
    LogicalIndexReport,
    LogicalIndexStatistics,
    QueryIndexPlan,
)
from .statistics import (
    CostEstimator,
    HistogramBuilder,
    StatisticsBuilder,
    StatisticsValidator,
)
from .statistics_errors import (
    CostEstimationError,
    InvalidStatisticsError,
    InvalidStatisticsPolicyError,
    StatisticsError,
    StatisticsValidationError,
)
from .statistics_models import (
    STATISTICS_SCHEMA_VERSION,
    AttributeStatistics,
    CostEstimate,
    EstimationStrategy,
    Histogram,
    HistogramBucket,
    HistogramPolicy,
    LogicalStatistics,
    StatisticsPolicy,
    StatisticsReport,
)
from .planner import CostBasedPlanner, PLANNER_VERSION, PlannerValidator
from .planner_errors import (
    InvalidPlannerModelError,
    PlannerError,
    PlannerValidationError,
    PlanningError,
)
from .planner_models import (
    PLANNER_SCHEMA_VERSION,
    PlannerDecision,
    PlannerMetrics,
    PlannerPolicy,
    PlannerReport,
    PlannerWeights,
    QueryExecutionPlan,
    QueryExecutionStrategy,
)
from .optimizer import (
    OPTIMIZER_VERSION,
    OptimizationPipeline,
    OptimizerValidator,
)
from .optimizer_errors import (
    InvalidOptimizerModelError,
    OptimizationError,
    OptimizerError,
    OptimizerValidationError,
)
from .optimizer_models import (
    OPTIMIZER_SCHEMA_VERSION,
    OptimizationCategory,
    OptimizationContext,
    OptimizationDecision,
    OptimizationDecisionStatus,
    OptimizationMetrics,
    OptimizationReport,
    OptimizationResult,
)
from .optimizer_rules import (
    BooleanNormalizationRule,
    ConstantExpressionRule,
    DuplicateProjectionRemovalRule,
    EmptyPredicateRule,
    IdentityTransformationRule,
    LimitNormalizationRule,
    OptimizationRule,
    PredicateSimplificationRule,
    ProjectionNormalizationRule,
    RedundantFilterRemovalRule,
    SortNormalizationRule,
)
from .execution_errors import (
    ExecutionPlannerError,
    ExecutionPlanningError,
    ExecutionValidationError,
    InvalidExecutionModelError,
)
from .execution_models import (
    EXECUTION_SCHEMA_VERSION,
    CompositeIndexScanNode,
    ExecutionContext,
    ExecutionMetrics,
    ExecutionNode,
    ExecutionNodeType,
    ExecutionPlan,
    ExecutionReport,
    FilterNode,
    IndexScanNode,
    LimitNode,
    OrderedScanNode,
    PrefixScanNode,
    ProjectionNode,
    RootNode,
    ScanNode,
    SortNode,
)
from .execution_planner import (
    EXECUTION_PLANNER_VERSION,
    ExecutionPipeline,
    ExecutionPlanValidator,
    ExecutionValidator,
)
from .providers import (
    DiscoveryExecutionMode,
    DiscoveryProviderDescriptor,
    DiscoveryProviderFactory,
    DiscoveryProviderRegistry,
    DiscoveryProviderResolver,
)
from .service import DiscoveryService
from .session import (
    DiscoverySession,
    DiscoverySessionMetrics,
    DiscoverySessionState,
)
from .stream import DiscoveryStream
from .streaming_contracts import (
    AsyncBatchConsumer,
    AsyncBatchProducer,
    BatchConsumer,
    BatchConsumptionContext,
    BatchProducer,
    BatchProductionContext,
)
from .streaming_errors import (
    BackpressureViolationError,
    BatchConsumerError,
    BatchProducerError,
    DiscoveryStreamTransitionError,
    DuplicateBatchError,
    InvalidBatchAcknowledgementError,
    InvalidBatchCursorError,
    InvalidBatchSequenceError,
    InvalidDiscoveryStreamError,
)
from .streaming_models import (
    BATCH_CURSOR_SCHEMA_VERSION,
    BackpressurePolicy,
    BatchAcknowledgement,
    BatchAcknowledgementStatus,
    BatchCursor,
    ConsumerUnavailableBehavior,
    DiscoveryStreamState,
    StreamMetrics,
)
from .streaming_pipeline import StreamingDiscoveryPipeline, StreamingExecution
from .validator import DefaultDiscoveryValidator

__all__ = [
    "AttributeResolutionError", "AttributeResolver", "AttributeValue",
    "AsyncBatchConsumer", "AsyncBatchProducer", "AsyncDiscoveryProvider",
    "BATCH_CURSOR_SCHEMA_VERSION", "BackpressurePolicy",
    "BackpressureViolationError", "BatchAcknowledgement",
    "BatchAcknowledgementStatus", "BatchConsumer", "BatchConsumerError",
    "BatchConsumptionContext", "BatchCursor", "BatchProducer",
    "BatchProducerError", "BatchProductionContext",
    "CAPABILITY_SCHEMA_VERSION", "CancellationToken", "Capability",
    "CapabilityCategory", "CapabilityConflictError",
    "CapabilityDependencyError", "CapabilityError",
    "CapabilityNegotiationEngine", "CapabilityNegotiationError",
    "CapabilityReport", "CapabilityRequirement", "CapabilityRequirementType",
    "CapabilityResolver", "CapabilitySet", "CapabilityValidationEngine",
    "CapabilityValidationError",
    "CanonicalIdentityAllocator", "ConflictBehavior", "ConflictSeverity",
    "ConsumerUnavailableBehavior",
    "ContextualDiscoveryProvider",
    "DISCOVERY_BATCH_COMPLETED", "DISCOVERY_CANCELLED", "DISCOVERY_COMPLETED",
    "DISCOVERY_EVENT_NAMES", "DISCOVERY_FAILED", "DISCOVERY_ITEM_OBSERVED",
    "DISCOVERY_ITEM_REJECTED", "DISCOVERY_SCHEMA_VERSION", "DISCOVERY_STARTED",
    "DefaultDiscoveryAssetMapper", "DefaultDiscoveryValidator", "DiscoveredItem",
    "DefaultAttributeResolver", "DefaultQueryEvaluationStream",
    "DefaultCanonicalIdentityAllocator", "DefaultNeutralEvidenceEvaluator",
    "DiscoveryAssetMapper", "DiscoveryBatch", "DiscoveryCancelledError",
    "DiscoveryCapability", "DiscoveryCheckpoint", "DiscoveryContext",
    "DiscoveryError", "DiscoveryErrorRecord", "DiscoveryExecution",
    "DiscoveryExecutionContext", "DiscoveryExecutionError",
    "DiscoveryExecutionMode", "DiscoveryExecutor",
    "DiscoveryEventPublisher", "DiscoveryEvidence", "DiscoveryMappingError",
    "DiscoveryMetrics", "DiscoveryPipeline", "DiscoveryPolicy",
    "DiscoveryProvider", "DiscoveryProviderDescriptor", "DiscoveryProviderError",
    "DiscoveryProviderFactory", "DiscoveryProviderNotFoundError",
    "DiscoveryProviderRegistrationError", "DiscoveryProviderRegistry",
    "DiscoveryProviderResolutionError", "DiscoveryProviderResolver",
    "DiscoveryRequest", "DiscoveryResult", "DiscoveryScope", "DiscoveryService",
    "DiscoverySession", "DiscoverySessionMetrics", "DiscoverySessionState",
    "DiscoverySessionStateError", "DiscoverySource", "DiscoverySourceId",
    "DiscoveryStream", "DiscoveryStreamState", "DiscoveryStreamTransitionError",
    "DiscoveryStatus", "DiscoveryValidationError", "DiscoveryValidator",
    "DuplicateBatchError",
    "EvaluationErrorBehavior", "FilterGroupEvaluationError",
    "InvalidBatchAcknowledgementError", "InvalidBatchCursorError",
    "InvalidBatchSequenceError", "InvalidDiscoveryStreamError",
    "InvalidCapabilityError",
    "IncompatibleTypeBehavior", "InvalidQueryEvaluationPolicyError",
    "InvalidQueryEvaluationSubjectError",
    "DiscoveryWarning", "InvalidDiscoveredItemError",
    "DiscoveryQuery", "FilterGroup", "FilterGroupOperator",
    "EvidenceEvaluation", "IDENTITY_RESOLUTION_SCHEMA_VERSION",
    "IdentityAllocationError", "IdentityAmbiguityError", "IdentityCandidate",
    "IdentityCandidateProvider", "IdentityCandidateProviderError",
    "IdentityConflict", "IdentityConflictError", "IdentityEvidence",
    "IdentityEvidenceEvaluationError", "IdentityEvidenceEvaluator",
    "IdentityEvidenceType", "IdentityFingerprint", "IdentityResolutionCancelledError",
    "IdentityResolutionEngine", "IdentityResolutionError", "IdentityResolutionRequest",
    "InsufficientEvidenceBehavior", "InvalidIdentityCandidateError",
    "InvalidIdentityEvidenceError", "InvalidIdentityPolicyError",
    "InvalidIdentityResolutionRequestError", "ResolutionDecision",
    "InvalidFilterError", "InvalidOrderingError", "InvalidPaginationError",
    "InvalidProjectionError", "InvalidQueryError", "QUERY_SCHEMA_VERSION",
    "MappingQueryEvaluationSubject", "MissingAttributeBehavior",
    "OrderingValuePosition", "PredicateEvaluationError",
    "PredicateEvaluationRecord", "ProjectedQueryItem",
    "QUERY_EVALUATION_SCHEMA_VERSION",
    "QueryEvaluationCancelledError", "QueryEvaluationContext",
    "QueryEvaluationEngine", "QueryEvaluationError",
    "QueryEvaluationLimitError", "QueryEvaluationPolicy",
    "QueryEvaluationResult", "QueryEvaluationStream",
    "QueryEvaluationSubject", "QueryMatchResult",
    "QueryOrderingEngine", "QueryOrderingEvaluationError",
    "QueryPaginationEngine", "QueryPaginationEvaluationError",
    "QueryPredicateEvaluator", "QueryProjectionEngine",
    "QueryProjectionEvaluationError",
    "QUERY_INDEX_SCHEMA_VERSION", "DiscardedLogicalIndex",
    "DuplicateBehavior", "IndexStrategy", "InvalidLogicalIndexError",
    "InvalidLogicalIndexPolicyError", "LogicalIndex", "LogicalIndexBuilder",
    "LogicalIndexEntry", "LogicalIndexError", "LogicalIndexPolicy",
    "LogicalIndexReport", "LogicalIndexResolutionError",
    "LogicalIndexResolver", "LogicalIndexStatistics",
    "LogicalIndexValidationError", "LogicalIndexValidator",
    "QueryIndexPlan", "QueryIndexPlanner",
    "QueryError", "QueryFilter", "QueryOperator", "QueryOrdering",
    "QueryOrderingDirection", "QueryPagination", "QueryPlan",
    "QueryProjection", "QueryResolutionError", "QueryResolver",
    "QueryValidationEngine", "QueryValidationError",
    "ResolutionPolicy", "ResolutionStatus",
    "InvalidDiscoveryRequestError", "InvalidDiscoverySourceError",
    "StreamMetrics", "StreamingDiscoveryPipeline", "StreamingExecution",
    "UnsupportedDiscoveryCapabilityError", "create_discovery_event",
    "discovery_model_from_dict", "ensure_supported_capabilities", "validate_policy",
]

__all__ += [
    "AttributeStatistics", "CostEstimate", "CostEstimationError",
    "CostEstimator", "EstimationStrategy", "Histogram", "HistogramBucket",
    "HistogramBuilder", "HistogramPolicy", "InvalidStatisticsError",
    "InvalidStatisticsPolicyError", "LogicalStatistics",
    "STATISTICS_SCHEMA_VERSION", "StatisticsBuilder", "StatisticsError",
    "StatisticsPolicy", "StatisticsReport", "StatisticsValidationError",
    "StatisticsValidator",
]

__all__ += [
    "CostBasedPlanner", "InvalidPlannerModelError", "PLANNER_SCHEMA_VERSION",
    "PLANNER_VERSION", "PlannerDecision", "PlannerError", "PlannerMetrics",
    "PlannerPolicy", "PlannerReport", "PlannerValidationError",
    "PlannerValidator", "PlannerWeights", "PlanningError",
    "QueryExecutionPlan", "QueryExecutionStrategy",
]

__all__ += [
    "BooleanNormalizationRule", "ConstantExpressionRule",
    "DuplicateProjectionRemovalRule", "EmptyPredicateRule",
    "IdentityTransformationRule", "InvalidOptimizerModelError",
    "LimitNormalizationRule", "OPTIMIZER_SCHEMA_VERSION",
    "OPTIMIZER_VERSION", "OptimizationCategory", "OptimizationContext",
    "OptimizationDecision", "OptimizationDecisionStatus", "OptimizationError",
    "OptimizationMetrics", "OptimizationPipeline", "OptimizationReport",
    "OptimizationResult", "OptimizationRule", "OptimizerError",
    "OptimizerValidationError", "OptimizerValidator",
    "PredicateSimplificationRule", "ProjectionNormalizationRule",
    "RedundantFilterRemovalRule", "SortNormalizationRule",
]

__all__ += [
    "EXECUTION_PLANNER_VERSION", "EXECUTION_SCHEMA_VERSION",
    "CompositeIndexScanNode", "ExecutionContext", "ExecutionMetrics",
    "ExecutionNode", "ExecutionNodeType", "ExecutionPipeline", "ExecutionPlan",
    "ExecutionPlannerError", "ExecutionPlanningError", "ExecutionPlanValidator",
    "ExecutionReport", "ExecutionValidationError", "ExecutionValidator",
    "FilterNode", "IndexScanNode", "InvalidExecutionModelError", "LimitNode",
    "OrderedScanNode", "PrefixScanNode", "ProjectionNode", "RootNode",
    "ScanNode", "SortNode",
]
