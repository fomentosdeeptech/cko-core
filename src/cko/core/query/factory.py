"""Mandatory validated creation boundary for canonical query intent."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable, Mapping

from .enums import (
    QueryConsistency, QueryDirection, QueryOperator, QueryScope, QueryStatus,
    QueryTarget,
)
from .errors import QueryError, QueryFactoryError
from .identity import QueryId, QueryIdentity
from .metadata import QueryMetadata
from .models import (
    _FACTORY_TOKEN, CanonicalQuery, QueryCollection, QueryConstraint,
    QueryDescriptor, QueryExpression, QueryFilter, QueryItem, QueryOrdering,
    QueryPagination, QueryProjection, QueryResult, QueryStatistics,
)
from .validator import QueryValidator


class QueryFactory:
    """Create every query model through one structural validation boundary."""

    def __init__(self, validator: QueryValidator | None = None,
                 clock: Callable[[], datetime] | None = None) -> None:
        self._validator = validator or QueryValidator()
        self._clock = clock or (lambda: datetime.now(UTC))

    def create_constraint(self, operator: QueryOperator, value: object,
                          upper_value: object | None = None) -> QueryConstraint:
        model = QueryConstraint(operator, value, upper_value)
        self._validator.validate(model)
        return model

    def create_filter(self, field: str, operator: QueryOperator, value: object,
                      upper_value: object | None = None) -> QueryFilter:
        model = QueryFilter(field, self.create_constraint(operator, value, upper_value))
        self._validator.validate(model)
        return model

    def create_expression(self, operator: QueryOperator,
                          clauses: tuple[QueryFilter | QueryExpression, ...]) -> QueryExpression:
        model = QueryExpression(operator, clauses)
        self._validator.validate(model)
        return model

    def create_ordering(self, field: str,
                        direction: QueryDirection = QueryDirection.ASCENDING,
                        priority: int = 0) -> QueryOrdering:
        model = QueryOrdering(field, direction, priority)
        self._validator.validate(model)
        return model

    def create_projection(self, fields: tuple[str, ...] = (), *,
                          include_identity: bool = True,
                          include_metadata: bool = True) -> QueryProjection:
        model = QueryProjection(fields, include_identity, include_metadata)
        self._validator.validate(model)
        return model

    def create_pagination(self, limit: int = 100, offset: int = 0,
                          cursor: str | None = None) -> QueryPagination:
        model = QueryPagination(limit, offset, cursor)
        self._validator.validate(model)
        return model

    def create_descriptor(
        self,
        *,
        targets: tuple[QueryTarget, ...],
        scope: QueryScope = QueryScope.CURRENT_NAMESPACE,
        consistency: QueryConsistency = QueryConsistency.DECLARED,
        filters: tuple[QueryFilter, ...] = (),
        expression: QueryExpression | None = None,
        orderings: tuple[QueryOrdering, ...] = (),
        projection: QueryProjection | None = None,
        pagination: QueryPagination | None = None,
    ) -> QueryDescriptor:
        model = QueryDescriptor(
            targets, scope, consistency, filters, expression, orderings,
            projection or self.create_projection(),
            pagination or self.create_pagination(),
        )
        self._validator.validate(model)
        return model

    def create(
        self,
        *,
        namespace: str,
        name: str,
        created_by: str,
        targets: tuple[QueryTarget, ...],
        scope: QueryScope = QueryScope.CURRENT_NAMESPACE,
        consistency: QueryConsistency = QueryConsistency.DECLARED,
        filters: tuple[QueryFilter, ...] = (),
        expression: QueryExpression | None = None,
        orderings: tuple[QueryOrdering, ...] = (),
        projection: QueryProjection | None = None,
        pagination: QueryPagination | None = None,
        status: QueryStatus = QueryStatus.READY,
        tags: tuple[str, ...] = (),
        attributes: Mapping[str, object] | None = None,
        version: str = "1.0.0",
        logical_id: QueryId | None = None,
    ) -> CanonicalQuery:
        try:
            selected_id = logical_id or QueryId.new()
            identity = QueryIdentity(
                selected_id,
                QueryId.canonical(namespace, f"{selected_id}:{name}"),
                namespace,
                name,
                version,
            )
            now = self._clock()
            metadata = QueryMetadata(
                now, now, created_by, status, tags, attributes or {},
            )
            descriptor = self.create_descriptor(
                targets=targets, scope=scope, consistency=consistency,
                filters=filters, expression=expression, orderings=orderings,
                projection=projection, pagination=pagination,
            )
            return self.from_parts(
                identity=identity, metadata=metadata, descriptor=descriptor,
            )
        except QueryError:
            raise
        except Exception as error:
            raise QueryFactoryError("canonical query creation failed") from error

    def from_parts(self, *, identity: QueryIdentity, metadata: QueryMetadata,
                   descriptor: QueryDescriptor) -> CanonicalQuery:
        model = CanonicalQuery(
            identity, metadata, descriptor, _factory_token=_FACTORY_TOKEN,
        )
        self._validator.validate(model)
        return model

    def create_statistics(self, total_expected: int | None = None,
                          total_returned: int = 0, logical_time: float = 0.0,
                          metrics: Mapping[str, object] | None = None) -> QueryStatistics:
        model = QueryStatistics(
            total_expected, total_returned, logical_time, metrics or {},
        )
        self._validator.validate(model)
        return model

    def create_result(
        self,
        query: CanonicalQuery,
        items: tuple[QueryItem, ...] = (),
        *,
        status: QueryStatus = QueryStatus.COMPLETED,
        total_expected: int | None = None,
        logical_time: float = 0.0,
        metrics: Mapping[str, object] | None = None,
        warnings: tuple[str, ...] = (),
        metadata: Mapping[str, object] | None = None,
    ) -> QueryResult:
        statistics = self.create_statistics(
            total_expected, len(items), logical_time, metrics,
        )
        model = QueryResult(
            query, items, status, total_expected, len(items), logical_time,
            statistics, warnings, metadata or {},
            _factory_token=_FACTORY_TOKEN,
        )
        self._validator.validate(model)
        return model

    def result_from_parts(
        self,
        *,
        query: CanonicalQuery,
        items: tuple[QueryItem, ...],
        status: QueryStatus,
        statistics: QueryStatistics,
        warnings: tuple[str, ...],
        metadata: Mapping[str, object],
    ) -> QueryResult:
        model = QueryResult(
            query, items, status, statistics.total_expected,
            statistics.total_returned, statistics.logical_time,
            statistics, warnings, metadata,
            _factory_token=_FACTORY_TOKEN,
        )
        self._validator.validate(model)
        return model

    def create_collection(self, queries: tuple[CanonicalQuery, ...] = (),
                          name: str | None = None) -> QueryCollection:
        model = QueryCollection(queries, name, _factory_token=_FACTORY_TOKEN)
        self._validator.validate(model)
        return model


__all__ = ["QueryFactory"]
