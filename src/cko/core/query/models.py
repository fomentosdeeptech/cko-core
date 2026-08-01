"""Canonical immutable models for technology-neutral query intent and results."""

from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from datetime import datetime
from typing import ClassVar, Mapping

from cko.core.documents import CanonicalDocument
from cko.core.graph import CanonicalGraph
from cko.core.knowledge import KnowledgeObject
from cko.core.relationships import CanonicalRelationship

from .contracts import (
    QUERY_SCHEMA_VERSION, QueryModel, deep_freeze, finite_number,
    model_sequence, non_negative_int, query_value_primitive, text, unique_texts,
)
from .enums import (
    QueryConsistency, QueryDirection, QueryOperator, QueryScope, QueryStatus,
    QueryTarget,
)
from .errors import QueryFactoryError, QueryValidationError
from .identity import QueryIdentity
from .metadata import QueryMetadata


_FACTORY_TOKEN = object()
_LOGICAL_OPERATORS = {QueryOperator.AND, QueryOperator.OR, QueryOperator.NOT}
_COMPARISON_OPERATORS = set(QueryOperator) - _LOGICAL_OPERATORS
_FILTER_ROOTS = {
    "identity", "namespace", "type", "category", "author", "origin",
    "version", "status", "created_at", "modified_at", "temporal", "tags",
    "keywords", "attributes", "properties",
}


def _enum(value: object, enum_type: type, name: str):
    try:
        return enum_type(value)
    except (TypeError, ValueError) as error:
        raise QueryValidationError(f"{name} contains an invalid enum") from error


def _query_value(value: object, name: str) -> object:
    try:
        return deep_freeze(value)
    except QueryValidationError as error:
        raise QueryValidationError(f"invalid {name}") from error


@dataclass(frozen=True, slots=True)
class QueryConstraint(QueryModel):
    operator: QueryOperator
    value: object
    upper_value: object | None = None
    schema_version: str = QUERY_SCHEMA_VERSION
    discriminator: ClassVar[str] = "query_constraint"

    def __post_init__(self) -> None:
        operator = _enum(self.operator, QueryOperator, "operator")
        if operator not in _COMPARISON_OPERATORS:
            raise QueryValidationError("constraint operator must be a comparison operator")
        object.__setattr__(self, "operator", operator)
        object.__setattr__(self, "value", _query_value(self.value, "constraint value"))
        object.__setattr__(self, "upper_value", _query_value(self.upper_value, "upper value"))
        if operator is QueryOperator.BETWEEN:
            if self.value is None or self.upper_value is None:
                raise QueryValidationError("between requires lower and upper values")
            if type(self.value) is not type(self.upper_value):
                raise QueryValidationError("between boundaries must have the same type")
            try:
                if self.value > self.upper_value:
                    raise QueryValidationError("between lower value cannot exceed upper value")
            except TypeError as error:
                raise QueryValidationError("between boundaries must be comparable") from error
        elif self.upper_value is not None:
            raise QueryValidationError("upper_value is exclusive to between")
        if operator is QueryOperator.IN:
            if not isinstance(self.value, tuple) or not self.value:
                raise QueryValidationError("in requires a non-empty sequence value")
        if operator in {QueryOperator.STARTS_WITH, QueryOperator.ENDS_WITH}:
            if not isinstance(self.value, str):
                raise QueryValidationError("prefix and suffix operators require a string value")
        self._validate_schema()

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "model": self.model,
            "operator": self.operator.value,
            "value": query_value_primitive(self.value),
            "upper_value": query_value_primitive(self.upper_value),
        }


@dataclass(frozen=True, slots=True)
class QueryFilter(QueryModel):
    field: str
    constraint: QueryConstraint
    schema_version: str = QUERY_SCHEMA_VERSION
    discriminator: ClassVar[str] = "query_filter"

    def __post_init__(self) -> None:
        normalized = text(self.field, "field")
        assert isinstance(normalized, str)
        root = normalized.split(".", 1)[0]
        if root not in _FILTER_ROOTS:
            raise QueryValidationError("field is not an official query filter dimension")
        if root in {"attributes", "properties"} and "." not in normalized:
            raise QueryValidationError("attribute and property filters require a named path")
        if not isinstance(self.constraint, QueryConstraint):
            raise QueryValidationError("constraint must be QueryConstraint")
        if root in {"created_at", "modified_at", "temporal"}:
            values = (self.constraint.value, self.constraint.upper_value)
            if any(value is not None and not isinstance(value, datetime) for value in values):
                raise QueryValidationError("temporal filters require UTC instants")
        object.__setattr__(self, "field", normalized)
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class QueryExpression(QueryModel):
    operator: QueryOperator
    clauses: tuple[QueryFilter | "QueryExpression", ...]
    schema_version: str = QUERY_SCHEMA_VERSION
    discriminator: ClassVar[str] = "query_expression"

    def __post_init__(self) -> None:
        operator = _enum(self.operator, QueryOperator, "operator")
        if operator not in _LOGICAL_OPERATORS:
            raise QueryValidationError("expression operator must be AND, OR, or NOT")
        object.__setattr__(self, "operator", operator)
        if not isinstance(self.clauses, (tuple, list)):
            raise QueryValidationError("clauses must be a sequence")
        clauses = tuple(self.clauses)
        if any(not isinstance(item, (QueryFilter, QueryExpression)) for item in clauses):
            raise QueryValidationError("clauses contain an invalid query model")
        if operator is QueryOperator.NOT and len(clauses) != 1:
            raise QueryValidationError("NOT requires exactly one clause")
        if operator in {QueryOperator.AND, QueryOperator.OR} and len(clauses) < 2:
            raise QueryValidationError("AND and OR require at least two clauses")
        object.__setattr__(self, "clauses", clauses)
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class QueryOrdering(QueryModel):
    field: str
    direction: QueryDirection = QueryDirection.ASCENDING
    priority: int = 0
    schema_version: str = QUERY_SCHEMA_VERSION
    discriminator: ClassVar[str] = "query_ordering"

    def __post_init__(self) -> None:
        object.__setattr__(self, "field", text(self.field, "field"))
        object.__setattr__(self, "direction", _enum(self.direction, QueryDirection, "direction"))
        object.__setattr__(self, "priority", non_negative_int(self.priority, "priority"))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class QueryProjection(QueryModel):
    fields: tuple[str, ...] = ()
    include_identity: bool = True
    include_metadata: bool = True
    schema_version: str = QUERY_SCHEMA_VERSION
    discriminator: ClassVar[str] = "query_projection"

    def __post_init__(self) -> None:
        object.__setattr__(self, "fields", unique_texts(self.fields, "fields"))
        if not isinstance(self.include_identity, bool) or not isinstance(self.include_metadata, bool):
            raise QueryValidationError("projection flags must be boolean")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class QueryPagination(QueryModel):
    limit: int = 100
    offset: int = 0
    cursor: str | None = None
    schema_version: str = QUERY_SCHEMA_VERSION
    discriminator: ClassVar[str] = "query_pagination"

    def __post_init__(self) -> None:
        object.__setattr__(self, "limit", non_negative_int(self.limit, "limit"))
        object.__setattr__(self, "offset", non_negative_int(self.offset, "offset"))
        object.__setattr__(self, "cursor", text(self.cursor, "cursor", optional=True))
        if self.limit == 0:
            raise QueryValidationError("limit must be greater than zero")
        if self.cursor is not None and self.offset != 0:
            raise QueryValidationError("cursor and non-zero offset are mutually exclusive")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class QueryDescriptor(QueryModel):
    targets: tuple[QueryTarget, ...]
    scope: QueryScope = QueryScope.CURRENT_NAMESPACE
    consistency: QueryConsistency = QueryConsistency.DECLARED
    filters: tuple[QueryFilter, ...] = ()
    expression: QueryExpression | None = None
    orderings: tuple[QueryOrdering, ...] = ()
    projection: QueryProjection = field(default_factory=QueryProjection)
    pagination: QueryPagination = field(default_factory=QueryPagination)
    schema_version: str = QUERY_SCHEMA_VERSION
    discriminator: ClassVar[str] = "query_descriptor"

    def __post_init__(self) -> None:
        if not isinstance(self.targets, (tuple, list)):
            raise QueryValidationError("targets must be a sequence")
        try:
            targets = tuple(QueryTarget(item) for item in self.targets)
        except (TypeError, ValueError) as error:
            raise QueryValidationError("targets contain an invalid enum") from error
        if not targets:
            raise QueryValidationError("targets must not be empty")
        if len(targets) != len(set(targets)):
            raise QueryValidationError("targets must not contain duplicates")
        object.__setattr__(self, "targets", targets)
        object.__setattr__(self, "scope", _enum(self.scope, QueryScope, "scope"))
        object.__setattr__(self, "consistency", _enum(self.consistency, QueryConsistency, "consistency"))
        object.__setattr__(self, "filters", model_sequence(self.filters, "filters", QueryFilter))
        if self.expression is not None and not isinstance(self.expression, QueryExpression):
            raise QueryValidationError("expression must be QueryExpression")
        object.__setattr__(self, "orderings", model_sequence(self.orderings, "orderings", QueryOrdering))
        if not isinstance(self.projection, QueryProjection):
            raise QueryValidationError("projection must be QueryProjection")
        if not isinstance(self.pagination, QueryPagination):
            raise QueryValidationError("pagination must be QueryPagination")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class CanonicalQuery(QueryModel):
    identity: QueryIdentity
    metadata: QueryMetadata
    descriptor: QueryDescriptor
    schema_version: str = QUERY_SCHEMA_VERSION
    _factory_token: InitVar[object | None] = None
    discriminator: ClassVar[str] = "canonical_query"

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _FACTORY_TOKEN:
            raise QueryFactoryError("CanonicalQuery must be created by QueryFactory")
        if not isinstance(self.identity, QueryIdentity):
            raise QueryValidationError("identity must be QueryIdentity")
        if not isinstance(self.metadata, QueryMetadata):
            raise QueryValidationError("metadata must be QueryMetadata")
        if not isinstance(self.descriptor, QueryDescriptor):
            raise QueryValidationError("descriptor must be QueryDescriptor")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class QueryStatistics(QueryModel):
    total_expected: int | None = None
    total_returned: int = 0
    logical_time: float = 0.0
    metrics: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = QUERY_SCHEMA_VERSION
    discriminator: ClassVar[str] = "query_statistics"

    def __post_init__(self) -> None:
        object.__setattr__(self, "total_expected", non_negative_int(self.total_expected, "total_expected", optional=True))
        object.__setattr__(self, "total_returned", non_negative_int(self.total_returned, "total_returned"))
        object.__setattr__(self, "logical_time", finite_number(self.logical_time, "logical_time"))
        if self.logical_time < 0:
            raise QueryValidationError("logical_time must be non-negative")
        if self.total_expected is not None and self.total_expected < self.total_returned:
            raise QueryValidationError("total_expected cannot be smaller than total_returned")
        if not isinstance(self.metrics, Mapping):
            raise QueryValidationError("metrics must be a mapping")
        object.__setattr__(self, "metrics", deep_freeze(self.metrics))
        self._validate_schema()


QueryItem = KnowledgeObject | CanonicalDocument | CanonicalRelationship | CanonicalGraph


@dataclass(frozen=True, slots=True)
class QueryResult(QueryModel):
    query: CanonicalQuery
    items: tuple[QueryItem, ...] = ()
    status: QueryStatus = QueryStatus.COMPLETED
    total_expected: int | None = None
    total_returned: int = 0
    logical_time: float = 0.0
    statistics: QueryStatistics = field(default_factory=QueryStatistics)
    warnings: tuple[str, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = QUERY_SCHEMA_VERSION
    _factory_token: InitVar[object | None] = None
    discriminator: ClassVar[str] = "query_result"

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _FACTORY_TOKEN:
            raise QueryFactoryError("QueryResult must be created by QueryFactory")
        if not isinstance(self.query, CanonicalQuery):
            raise QueryValidationError("query must be CanonicalQuery")
        if not isinstance(self.items, (tuple, list)):
            raise QueryValidationError("items must be a sequence")
        accepted = (KnowledgeObject, CanonicalDocument, CanonicalRelationship, CanonicalGraph)
        items = tuple(self.items)
        if any(not isinstance(item, accepted) for item in items):
            raise QueryValidationError("items contain a non-homologated canonical model")
        object.__setattr__(self, "items", items)
        object.__setattr__(self, "status", _enum(self.status, QueryStatus, "status"))
        object.__setattr__(self, "total_expected", non_negative_int(self.total_expected, "total_expected", optional=True))
        object.__setattr__(self, "total_returned", non_negative_int(self.total_returned, "total_returned"))
        object.__setattr__(self, "logical_time", finite_number(self.logical_time, "logical_time"))
        if self.logical_time < 0:
            raise QueryValidationError("logical_time must be non-negative")
        if self.total_expected is not None and self.total_expected < self.total_returned:
            raise QueryValidationError("total_expected cannot be smaller than total_returned")
        if self.total_returned != len(items):
            raise QueryValidationError("total_returned must equal item count")
        if not isinstance(self.statistics, QueryStatistics):
            raise QueryValidationError("statistics must be QueryStatistics")
        if (self.statistics.total_expected != self.total_expected or
                self.statistics.total_returned != self.total_returned or
                self.statistics.logical_time != self.logical_time):
            raise QueryValidationError("statistics must match result totals and logical time")
        object.__setattr__(self, "warnings", unique_texts(self.warnings, "warnings"))
        if not isinstance(self.metadata, Mapping):
            raise QueryValidationError("metadata must be a mapping")
        object.__setattr__(self, "metadata", deep_freeze(self.metadata))
        self._validate_schema()

    def __iter__(self):
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)


@dataclass(frozen=True, slots=True)
class QueryCollection(QueryModel):
    queries: tuple[CanonicalQuery, ...] = ()
    name: str | None = None
    schema_version: str = QUERY_SCHEMA_VERSION
    _factory_token: InitVar[object | None] = None
    discriminator: ClassVar[str] = "query_collection"

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _FACTORY_TOKEN:
            raise QueryFactoryError("QueryCollection must be created by QueryFactory")
        object.__setattr__(self, "queries", model_sequence(self.queries, "queries", CanonicalQuery))
        object.__setattr__(self, "name", text(self.name, "name", optional=True))
        self._validate_schema()

    def __iter__(self):
        return iter(self.queries)

    def __len__(self) -> int:
        return len(self.queries)


__all__ = [
    "CanonicalQuery", "QueryCollection", "QueryConstraint", "QueryDescriptor",
    "QueryExpression", "QueryFilter", "QueryItem", "QueryOrdering",
    "QueryPagination", "QueryProjection", "QueryResult", "QueryStatistics",
    "_FACTORY_TOKEN",
]
