"""Deterministic logical resolution of canonical Discovery queries."""

from __future__ import annotations

from datetime import datetime

from cko.core.logging import get_logger
from cko.core.utils import utc_now

from .query_errors import QueryError, QueryResolutionError
from .query_models import (
    DiscoveryQuery,
    FilterGroup,
    QueryExpression,
    QueryPagination,
    QueryPlan,
)
from .query_validation import QueryValidationEngine


class QueryResolver:
    """Resolve a canonical query into an auditable neutral logical plan."""

    def __init__(
        self,
        validator: QueryValidationEngine | None = None,
    ) -> None:
        """Create a resolver with an injectable pure validation engine."""
        self._validator = validator or QueryValidationEngine()
        self._logger = get_logger("core.discovery.query")

    def resolve(
        self,
        query: DiscoveryQuery,
        *,
        timestamp: datetime | None = None,
    ) -> QueryPlan:
        """Validate and resolve a query without any infrastructure access."""
        query_id = query.id if isinstance(query, DiscoveryQuery) else None
        self._logger.info(
            "query resolution started",
            extra={
                "event": "discovery.query.resolution.started",
                "context": {"query_id": query_id},
            },
        )
        try:
            validated = self._validator.validate(query)
            pagination = self._effective_pagination(validated)
            plan = QueryPlan(
                query_id=validated.id,
                effective_filters=validated.filters,
                projections=validated.projections,
                ordering=tuple(
                    sorted(validated.ordering, key=lambda item: item.priority)
                ),
                pagination=pagination,
                estimates=self._estimates(validated.filters, pagination),
                justifications=self._justifications(validated, pagination),
                timestamp=timestamp or utc_now(),
            )
        except QueryError:
            self._logger.warning(
                "query resolution rejected",
                extra={
                    "event": "discovery.query.resolution.rejected",
                    "context": {"query_id": query_id},
                },
            )
            raise
        except Exception as error:
            self._logger.error(
                "query resolution failed",
                extra={
                    "event": "discovery.query.resolution.failed",
                    "context": {"query_id": query_id},
                },
            )
            raise QueryResolutionError(
                "canonical query could not be resolved"
            ) from error
        self._logger.info(
            "query resolution completed",
            extra={
                "event": "discovery.query.resolution.completed",
                "context": {
                    "query_id": plan.query_id,
                    "filter_count": plan.estimates["filter_predicate_count"],
                    "projection_count": len(plan.projections),
                    "ordering_count": len(plan.ordering),
                    "paginated": plan.pagination is not None,
                },
            },
        )
        return plan

    @staticmethod
    def _effective_pagination(
        query: DiscoveryQuery,
    ) -> QueryPagination | None:
        source = query.pagination
        if source is None and query.limit is None and query.offset is None:
            return None
        page_offset = (
            (source.page - 1) * source.page_size
            if source is not None and source.page is not None
            else None
        )
        return QueryPagination(
            page=source.page if source is not None else None,
            page_size=source.page_size if source is not None else None,
            offset=(
                query.offset
                if query.offset is not None
                else source.offset
                if source is not None and source.offset is not None
                else page_offset if page_offset is not None else 0
            ),
            limit=(
                query.limit
                if query.limit is not None
                else source.limit
                if source is not None and source.limit is not None
                else source.page_size if source is not None else None
            ),
        )

    @classmethod
    def _estimates(
        cls,
        expressions: tuple[QueryExpression, ...],
        pagination: QueryPagination | None,
    ) -> dict[str, object]:
        predicate_count = sum(cls._predicate_count(item) for item in expressions)
        upper_bound = pagination.limit if pagination is not None else None
        return {
            "filter_predicate_count": predicate_count,
            "logical_group_count": sum(
                cls._group_count(item) for item in expressions
            ),
            "result_cardinality_upper_bound": upper_bound,
        }

    @staticmethod
    def _justifications(
        query: DiscoveryQuery,
        pagination: QueryPagination | None,
    ) -> tuple[str, ...]:
        reasons = [
            "top-level filters are combined by implicit AND",
            (
                "explicit projections preserved"
                if query.projections
                else "no explicit projection requested"
            ),
            (
                "ordering normalized by ascending priority"
                if query.ordering
                else "no explicit ordering requested"
            ),
            (
                "pagination normalized from canonical boundaries"
                if pagination is not None
                else "unbounded logical result requested"
            ),
        ]
        return tuple(reasons)

    @classmethod
    def _predicate_count(cls, expression: QueryExpression) -> int:
        if not isinstance(expression, FilterGroup):
            return 1
        return sum(cls._predicate_count(item) for item in expression.filters)

    @classmethod
    def _group_count(cls, expression: QueryExpression) -> int:
        if not isinstance(expression, FilterGroup):
            return 0
        return 1 + sum(cls._group_count(item) for item in expression.filters)


__all__ = ["QueryResolver"]
