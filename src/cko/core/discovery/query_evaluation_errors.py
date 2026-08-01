"""Public failures raised by canonical in-memory query evaluation."""

from .query_errors import QueryError


class QueryEvaluationError(QueryError):
    """Base failure for canonical query evaluation."""


class InvalidQueryEvaluationSubjectError(QueryEvaluationError, ValueError):
    """Raised when an evaluation subject violates the public contract."""


class InvalidQueryEvaluationPolicyError(QueryEvaluationError, ValueError):
    """Raised when an evaluation policy is invalid or inconsistent."""


class AttributeResolutionError(QueryEvaluationError):
    """Raised when a logical attribute cannot be safely resolved."""


class PredicateEvaluationError(QueryEvaluationError):
    """Raised when an atomic predicate cannot be evaluated safely."""


class FilterGroupEvaluationError(QueryEvaluationError):
    """Raised when a logical filter group cannot be evaluated."""


class QueryProjectionEvaluationError(QueryEvaluationError):
    """Raised when an approved subject cannot be projected."""


class QueryOrderingEvaluationError(QueryEvaluationError):
    """Raised when result values cannot be ordered safely."""


class QueryPaginationEvaluationError(QueryEvaluationError):
    """Raised when normalized pagination cannot be applied."""


class QueryEvaluationCancelledError(QueryEvaluationError):
    """Raised when cooperative query evaluation is cancelled."""


class QueryEvaluationLimitError(QueryEvaluationError):
    """Raised when the policy subject limit is exceeded."""


__all__ = [
    "AttributeResolutionError",
    "FilterGroupEvaluationError",
    "InvalidQueryEvaluationPolicyError",
    "InvalidQueryEvaluationSubjectError",
    "PredicateEvaluationError",
    "QueryEvaluationCancelledError",
    "QueryEvaluationError",
    "QueryEvaluationLimitError",
    "QueryOrderingEvaluationError",
    "QueryPaginationEvaluationError",
    "QueryProjectionEvaluationError",
]
