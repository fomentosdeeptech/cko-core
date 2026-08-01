"""Validation engine for canonical infrastructure-neutral queries."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from .query_errors import (
    InvalidFilterError,
    InvalidOrderingError,
    InvalidPaginationError,
    InvalidProjectionError,
    QueryValidationError,
)
from .query_models import (
    DiscoveryQuery,
    FilterGroup,
    FilterGroupOperator,
    QueryExpression,
    QueryFilter,
    QueryOperator,
    QueryOrdering,
    QueryPagination,
    QueryProjection,
)


class QueryValidationEngine:
    """Validate filters, projections, ordering and pagination consistently."""

    def validate(self, query: DiscoveryQuery) -> DiscoveryQuery:
        """Return the unchanged valid query or raise a public query error."""
        if not isinstance(query, DiscoveryQuery):
            raise QueryValidationError("query must be DiscoveryQuery")
        self.validate_filters(query.filters)
        self.validate_projections(query.projections)
        self.validate_ordering(query.ordering)
        self.validate_pagination(query)
        return query

    def validate_filters(
        self,
        expressions: Iterable[QueryExpression],
    ) -> tuple[QueryExpression, ...]:
        """Validate a recursive collection of canonical filter expressions."""
        declared = tuple(expressions)
        for expression in declared:
            self._validate_expression(expression)
        return declared

    def validate_projections(
        self,
        projections: Iterable[QueryProjection],
    ) -> tuple[QueryProjection, ...]:
        """Reject invalid or duplicate explicit projection attributes."""
        declared = tuple(projections)
        if any(not isinstance(item, QueryProjection) for item in declared):
            raise InvalidProjectionError(
                "projections must contain QueryProjection"
            )
        attributes = [item.attribute for item in declared]
        duplicates = self._duplicates(attributes)
        if duplicates:
            raise InvalidProjectionError(
                "duplicate projection attributes: " + ", ".join(duplicates)
            )
        return declared

    def validate_ordering(
        self,
        ordering: Iterable[QueryOrdering],
    ) -> tuple[QueryOrdering, ...]:
        """Reject duplicate ordering attributes or priorities."""
        declared = tuple(ordering)
        if any(not isinstance(item, QueryOrdering) for item in declared):
            raise InvalidOrderingError("ordering must contain QueryOrdering")
        attributes = [item.attribute for item in declared]
        duplicate_attributes = self._duplicates(attributes)
        if duplicate_attributes:
            raise InvalidOrderingError(
                "duplicate ordering attributes: "
                + ", ".join(duplicate_attributes)
            )
        priorities = [item.priority for item in declared]
        duplicate_priorities = self._duplicates(priorities)
        if duplicate_priorities:
            rendered = ", ".join(str(item) for item in duplicate_priorities)
            raise InvalidOrderingError(
                f"duplicate ordering priorities: {rendered}"
            )
        return tuple(sorted(declared, key=lambda item: item.priority))

    def validate_pagination(
        self,
        query: DiscoveryQuery,
    ) -> QueryPagination | None:
        """Validate page and offset declarations across the complete query."""
        if not isinstance(query, DiscoveryQuery):
            raise QueryValidationError("query must be DiscoveryQuery")
        pagination = query.pagination
        if pagination is None:
            if query.limit is None and query.offset is None:
                return None
            return QueryPagination(offset=query.offset or 0, limit=query.limit)
        if pagination.page is not None and pagination.offset is not None:
            expected = (pagination.page - 1) * pagination.page_size
            if pagination.offset != expected:
                raise InvalidPaginationError(
                    "pagination offset is inconsistent with page and page_size"
                )
        if pagination.page_size is not None and pagination.limit is not None:
            if pagination.page_size != pagination.limit:
                raise InvalidPaginationError(
                    "pagination limit is inconsistent with page_size"
                )
        if query.limit is not None and pagination.limit is not None:
            if query.limit != pagination.limit:
                raise InvalidPaginationError(
                    "query limit conflicts with pagination limit"
                )
        if query.offset is not None and pagination.offset is not None:
            if query.offset != pagination.offset:
                raise InvalidPaginationError(
                    "query offset conflicts with pagination offset"
                )
        return pagination

    def _validate_expression(self, expression: QueryExpression) -> None:
        if isinstance(expression, QueryFilter):
            self._validate_filter(expression)
            return
        if not isinstance(expression, FilterGroup):
            raise InvalidFilterError(
                "filters must contain QueryFilter or FilterGroup"
            )
        if (
            expression.operator is FilterGroupOperator.NOT
            and len(expression.filters) != 1
        ):
            raise InvalidFilterError(
                "NOT filter groups require exactly one member"
            )
        for member in expression.filters:
            self._validate_expression(member)

    @staticmethod
    def _validate_filter(query_filter: QueryFilter) -> None:
        operator = query_filter.operator
        value = query_filter.value
        if operator in {
            QueryOperator.CONTAINS,
            QueryOperator.STARTS_WITH,
            QueryOperator.ENDS_WITH,
        } and not isinstance(value, str):
            raise InvalidFilterError(
                f"operator {operator.value} requires a string value"
            )
        if operator in {
            QueryOperator.GREATER_THAN,
            QueryOperator.GREATER_OR_EQUAL,
            QueryOperator.LOWER_THAN,
            QueryOperator.LOWER_OR_EQUAL,
        } and (value is None or isinstance(value, (tuple, Mapping))):
            raise InvalidFilterError(
                f"operator {operator.value} requires a scalar value"
            )

    @staticmethod
    def _duplicates(values: Iterable[object]) -> tuple[object, ...]:
        seen: set[object] = set()
        duplicates: set[object] = set()
        for value in values:
            if value in seen:
                duplicates.add(value)
            seen.add(value)
        return tuple(sorted(duplicates, key=str))


__all__ = ["QueryValidationEngine"]
