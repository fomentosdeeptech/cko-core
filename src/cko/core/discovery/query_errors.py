"""Public errors for the canonical Discovery query foundation."""

from .errors import DiscoveryError


class QueryError(DiscoveryError):
    """Base error for every canonical query failure."""


class InvalidQueryError(QueryError, ValueError):
    """Raised when a query violates a structural invariant."""


class InvalidFilterError(InvalidQueryError):
    """Raised when a filter or logical filter group is invalid."""


class InvalidProjectionError(InvalidQueryError):
    """Raised when an explicit query projection is invalid."""


class InvalidOrderingError(InvalidQueryError):
    """Raised when a query ordering declaration is invalid."""


class InvalidPaginationError(InvalidQueryError):
    """Raised when pagination values are invalid or inconsistent."""


class QueryValidationError(QueryError):
    """Raised when cross-model query validation fails."""


class QueryResolutionError(QueryError):
    """Raised when a validated query cannot be resolved logically."""


__all__ = [
    "InvalidFilterError",
    "InvalidOrderingError",
    "InvalidPaginationError",
    "InvalidProjectionError",
    "InvalidQueryError",
    "QueryError",
    "QueryResolutionError",
    "QueryValidationError",
]
