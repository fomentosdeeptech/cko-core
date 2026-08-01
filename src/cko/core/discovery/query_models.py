"""Immutable, versioned models for infrastructure-neutral Discovery queries."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Self, TypeAlias

from .query_errors import (
    InvalidFilterError,
    InvalidOrderingError,
    InvalidPaginationError,
    InvalidProjectionError,
    InvalidQueryError,
)


QUERY_SCHEMA_VERSION = "1.0"


def _non_empty(value: object, name: str, error: type[ValueError]) -> str:
    if not isinstance(value, str) or not value.strip():
        raise error(f"{name} must be a non-empty string")
    return value.strip()


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidFilterError("query values must contain finite numbers")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, nested in value.items():
            normalized = _non_empty(key, "mapping key", InvalidFilterError)
            frozen[normalized] = _freeze(nested)
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    raise InvalidFilterError(
        f"unsupported canonical query value: {type(value).__name__}"
    )


def _primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, datetime):
        instant = value.astimezone(timezone.utc)
        return instant.isoformat().replace("+00:00", "Z")
    if isinstance(value, _QueryModel):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {
            key: _primitive(nested)
            for key, nested in sorted(value.items())
        }
    if isinstance(value, (list, tuple)):
        return [_primitive(item) for item in value]
    raise TypeError(f"unsupported query serialization value: {type(value).__name__}")


def _json_object(payload: str) -> Mapping[str, object]:
    try:
        decoded = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as error:
        raise InvalidQueryError("query JSON is invalid") from error
    if not isinstance(decoded, dict):
        raise InvalidQueryError("query JSON must contain an object")
    return decoded


def _envelope(
    payload: Mapping[str, object],
    model: str,
    names: tuple[str, ...],
    error: type[ValueError],
) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise error(f"{model} payload must be a mapping")
    expected = {"schema_version", "model", *names}
    actual = set(payload)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        details: list[str] = []
        if missing:
            details.append(f"missing fields: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown fields: {', '.join(unknown)}")
        raise error(f"invalid {model} envelope ({'; '.join(details)})")
    if payload["schema_version"] != QUERY_SCHEMA_VERSION:
        raise error("unsupported query schema version")
    if payload["model"] != model:
        raise error(f"payload does not represent {model}")
    return {name: payload[name] for name in names}


def _sequence(value: object, name: str, error: type[ValueError]) -> tuple[object, ...]:
    if not isinstance(value, list):
        raise error(f"{name} must be a JSON array")
    return tuple(value)


def _mapping_sequence(
    value: object,
    name: str,
    error: type[ValueError],
) -> tuple[Mapping[str, object], ...]:
    declared = _sequence(value, name, error)
    if any(not isinstance(item, Mapping) for item in declared):
        raise error(f"{name} must contain JSON objects")
    return declared


def _optional_int(
    value: object,
    name: str,
    error: type[ValueError],
    *,
    minimum: int,
) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise error(f"{name} must be an integer greater than or equal to {minimum}")
    return value


def _aware(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise InvalidQueryError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


class _QueryModel:
    model_name: ClassVar[str]
    schema_version: ClassVar[str] = QUERY_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """Serialize this model using the strict canonical query envelope."""
        return {
            "schema_version": self.schema_version,
            "model": self.model_name,
            **{
                item.name: _primitive(getattr(self, item.name))
                for item in fields(self)
            },
        }

    def to_json(self) -> str:
        """Serialize this model as deterministic UTF-8-compatible JSON."""
        return json.dumps(
            self.to_dict(),
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize this model from a strict JSON object."""
        return cls.from_dict(_json_object(payload))


class QueryOperator(str, Enum):
    """Canonical operators supported by infrastructure-neutral filters."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LOWER_THAN = "lower_than"
    LOWER_OR_EQUAL = "lower_or_equal"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"


class FilterGroupOperator(str, Enum):
    """Boolean operators used to compose filters recursively."""

    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class QueryOrderingDirection(str, Enum):
    """Canonical direction of a query ordering clause."""

    ASCENDING = "ascending"
    DESCENDING = "descending"


@dataclass(frozen=True, slots=True)
class QueryFilter(_QueryModel):
    """Atomic immutable predicate over one logical attribute."""

    model_name: ClassVar[str] = "query_filter"
    attribute: str
    operator: QueryOperator
    value: object = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "attribute",
            _non_empty(self.attribute, "attribute", InvalidFilterError),
        )
        try:
            operator = QueryOperator(self.operator)
        except (TypeError, ValueError) as error:
            raise InvalidFilterError("unsupported query filter operator") from error
        frozen = _freeze(self.value)
        if operator in {QueryOperator.EXISTS, QueryOperator.NOT_EXISTS}:
            if frozen is not None:
                raise InvalidFilterError(
                    f"operator {operator.value} does not accept a value"
                )
        elif operator in {QueryOperator.IN, QueryOperator.NOT_IN}:
            if not isinstance(frozen, tuple) or not frozen:
                raise InvalidFilterError(
                    f"operator {operator.value} requires a non-empty sequence"
                )
        object.__setattr__(self, "operator", operator)
        object.__setattr__(self, "value", frozen)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize an atomic filter from a strict mapping."""
        data = _envelope(
            payload,
            cls.model_name,
            ("attribute", "operator", "value"),
            InvalidFilterError,
        )
        return cls(**data)


QueryExpression: TypeAlias = "QueryFilter | FilterGroup"


@dataclass(frozen=True, slots=True)
class FilterGroup(_QueryModel):
    """Recursive immutable group of filters joined by AND, OR or NOT."""

    model_name: ClassVar[str] = "filter_group"
    operator: FilterGroupOperator
    filters: tuple[QueryExpression, ...]

    def __post_init__(self) -> None:
        try:
            operator = FilterGroupOperator(self.operator)
        except (TypeError, ValueError) as error:
            raise InvalidFilterError("unsupported filter group operator") from error
        members = tuple(self.filters)
        if not members or any(
            not isinstance(item, (QueryFilter, FilterGroup)) for item in members
        ):
            raise InvalidFilterError(
                "filter groups must contain canonical query expressions"
            )
        if operator is FilterGroupOperator.NOT and len(members) != 1:
            raise InvalidFilterError("NOT filter groups require exactly one member")
        object.__setattr__(self, "operator", operator)
        object.__setattr__(self, "filters", members)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a recursive filter group from a strict mapping."""
        data = _envelope(
            payload,
            cls.model_name,
            ("operator", "filters"),
            InvalidFilterError,
        )
        raw_filters = _sequence(
            data["filters"], "filters", InvalidFilterError
        )
        return cls(
            operator=data["operator"],
            filters=tuple(_expression_from_dict(item) for item in raw_filters),
        )


def _expression_from_dict(value: object) -> QueryExpression:
    if not isinstance(value, Mapping):
        raise InvalidFilterError("filter expressions must be mappings")
    model = value.get("model")
    if model == QueryFilter.model_name:
        return QueryFilter.from_dict(value)
    if model == FilterGroup.model_name:
        return FilterGroup.from_dict(value)
    raise InvalidFilterError("unknown filter expression model")


@dataclass(frozen=True, slots=True)
class QueryProjection(_QueryModel):
    """Explicit selection of one logical attribute."""

    model_name: ClassVar[str] = "query_projection"
    attribute: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "attribute",
            _non_empty(self.attribute, "attribute", InvalidProjectionError),
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a projection from a strict mapping."""
        data = _envelope(
            payload,
            cls.model_name,
            ("attribute",),
            InvalidProjectionError,
        )
        return cls(**data)


@dataclass(frozen=True, slots=True)
class QueryOrdering(_QueryModel):
    """Ordering declaration with an explicit deterministic priority."""

    model_name: ClassVar[str] = "query_ordering"
    attribute: str
    direction: QueryOrderingDirection = QueryOrderingDirection.ASCENDING
    priority: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "attribute",
            _non_empty(self.attribute, "attribute", InvalidOrderingError),
        )
        try:
            direction = QueryOrderingDirection(self.direction)
        except (TypeError, ValueError) as error:
            raise InvalidOrderingError("unsupported ordering direction") from error
        if isinstance(self.priority, bool) or not isinstance(self.priority, int):
            raise InvalidOrderingError("priority must be a non-negative integer")
        if self.priority < 0:
            raise InvalidOrderingError("priority must be a non-negative integer")
        object.__setattr__(self, "direction", direction)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize an ordering clause from a strict mapping."""
        data = _envelope(
            payload,
            cls.model_name,
            ("attribute", "direction", "priority"),
            InvalidOrderingError,
        )
        return cls(**data)


@dataclass(frozen=True, slots=True)
class QueryPagination(_QueryModel):
    """Optional page-based and offset-based pagination declaration."""

    model_name: ClassVar[str] = "query_pagination"
    page: int | None = None
    page_size: int | None = None
    offset: int | None = None
    limit: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "page",
            _optional_int(
                self.page, "page", InvalidPaginationError, minimum=1
            ),
        )
        object.__setattr__(
            self,
            "page_size",
            _optional_int(
                self.page_size,
                "page_size",
                InvalidPaginationError,
                minimum=1,
            ),
        )
        object.__setattr__(
            self,
            "offset",
            _optional_int(
                self.offset, "offset", InvalidPaginationError, minimum=0
            ),
        )
        object.__setattr__(
            self,
            "limit",
            _optional_int(
                self.limit, "limit", InvalidPaginationError, minimum=1
            ),
        )
        if (self.page is None) != (self.page_size is None):
            raise InvalidPaginationError(
                "page and page_size must be declared together"
            )
        if all(
            value is None
            for value in (self.page, self.page_size, self.offset, self.limit)
        ):
            raise InvalidPaginationError(
                "pagination must declare a page or offset boundary"
            )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize pagination from a strict mapping."""
        data = _envelope(
            payload,
            cls.model_name,
            ("page", "page_size", "offset", "limit"),
            InvalidPaginationError,
        )
        return cls(**data)


@dataclass(frozen=True, slots=True)
class DiscoveryQuery(_QueryModel):
    """Canonical immutable description of a Discovery query."""

    model_name: ClassVar[str] = "discovery_query"
    id: str
    name: str
    description: str
    filters: tuple[QueryExpression, ...] = ()
    projections: tuple[QueryProjection, ...] = ()
    ordering: tuple[QueryOrdering, ...] = ()
    pagination: QueryPagination | None = None
    limit: int | None = None
    offset: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "id", _non_empty(self.id, "id", InvalidQueryError)
        )
        object.__setattr__(
            self, "name", _non_empty(self.name, "name", InvalidQueryError)
        )
        object.__setattr__(
            self,
            "description",
            _non_empty(self.description, "description", InvalidQueryError),
        )
        expressions = tuple(self.filters)
        projections = tuple(self.projections)
        ordering = tuple(self.ordering)
        if any(
            not isinstance(item, (QueryFilter, FilterGroup))
            for item in expressions
        ):
            raise InvalidQueryError("filters contain a non-canonical expression")
        if any(not isinstance(item, QueryProjection) for item in projections):
            raise InvalidQueryError("projections contain an invalid model")
        if any(not isinstance(item, QueryOrdering) for item in ordering):
            raise InvalidQueryError("ordering contains an invalid model")
        if self.pagination is not None and not isinstance(
            self.pagination, QueryPagination
        ):
            raise InvalidQueryError("pagination must be QueryPagination")
        object.__setattr__(self, "filters", expressions)
        object.__setattr__(self, "projections", projections)
        object.__setattr__(self, "ordering", ordering)
        object.__setattr__(
            self,
            "limit",
            _optional_int(
                self.limit, "limit", InvalidQueryError, minimum=1
            ),
        )
        object.__setattr__(
            self,
            "offset",
            _optional_int(
                self.offset, "offset", InvalidQueryError, minimum=0
            ),
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a query from a strict canonical mapping."""
        data = _envelope(
            payload,
            cls.model_name,
            (
                "id", "name", "description", "filters", "projections",
                "ordering", "pagination", "limit", "offset",
            ),
            InvalidQueryError,
        )
        raw_filters = _sequence(data["filters"], "filters", InvalidQueryError)
        raw_projections = _mapping_sequence(
            data["projections"], "projections", InvalidQueryError
        )
        raw_ordering = _mapping_sequence(
            data["ordering"], "ordering", InvalidQueryError
        )
        pagination = data["pagination"]
        if pagination is not None and not isinstance(pagination, Mapping):
            raise InvalidPaginationError("pagination must be a mapping")
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            filters=tuple(_expression_from_dict(item) for item in raw_filters),
            projections=tuple(
                QueryProjection.from_dict(item) for item in raw_projections
            ),
            ordering=tuple(
                QueryOrdering.from_dict(item) for item in raw_ordering
            ),
            pagination=(
                QueryPagination.from_dict(pagination)
                if pagination is not None
                else None
            ),
            limit=data["limit"],
            offset=data["offset"],
        )


@dataclass(frozen=True, slots=True)
class QueryPlan(_QueryModel):
    """Auditable, infrastructure-neutral logical resolution of a query."""

    model_name: ClassVar[str] = "query_plan"
    query_id: str
    effective_filters: tuple[QueryExpression, ...]
    projections: tuple[QueryProjection, ...]
    ordering: tuple[QueryOrdering, ...]
    pagination: QueryPagination | None
    estimates: Mapping[str, object] = field(default_factory=dict)
    justifications: tuple[str, ...] = ()
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "query_id",
            _non_empty(self.query_id, "query_id", InvalidQueryError),
        )
        expressions = tuple(self.effective_filters)
        projections = tuple(self.projections)
        ordering = tuple(self.ordering)
        if any(
            not isinstance(item, (QueryFilter, FilterGroup))
            for item in expressions
        ):
            raise InvalidQueryError("effective_filters are invalid")
        if any(not isinstance(item, QueryProjection) for item in projections):
            raise InvalidQueryError("plan projections are invalid")
        if any(not isinstance(item, QueryOrdering) for item in ordering):
            raise InvalidQueryError("plan ordering is invalid")
        if self.pagination is not None and not isinstance(
            self.pagination, QueryPagination
        ):
            raise InvalidQueryError("plan pagination is invalid")
        reasons = tuple(
            _non_empty(item, "justification", InvalidQueryError)
            for item in self.justifications
        )
        object.__setattr__(self, "effective_filters", expressions)
        object.__setattr__(self, "projections", projections)
        object.__setattr__(
            self,
            "ordering",
            tuple(sorted(ordering, key=lambda item: item.priority)),
        )
        object.__setattr__(self, "estimates", _freeze(self.estimates))
        object.__setattr__(self, "justifications", reasons)
        object.__setattr__(self, "timestamp", _aware(self.timestamp))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize an auditable query plan from a strict mapping."""
        data = _envelope(
            payload,
            cls.model_name,
            (
                "query_id", "effective_filters", "projections", "ordering",
                "pagination", "estimates", "justifications", "timestamp",
            ),
            InvalidQueryError,
        )
        filters = _sequence(
            data["effective_filters"],
            "effective_filters",
            InvalidQueryError,
        )
        projections = _mapping_sequence(
            data["projections"], "projections", InvalidQueryError
        )
        ordering = _mapping_sequence(
            data["ordering"], "ordering", InvalidQueryError
        )
        reasons = _sequence(
            data["justifications"], "justifications", InvalidQueryError
        )
        pagination = data["pagination"]
        if pagination is not None and not isinstance(pagination, Mapping):
            raise InvalidPaginationError("plan pagination must be a mapping")
        estimates = data["estimates"]
        if not isinstance(estimates, Mapping):
            raise InvalidQueryError("estimates must be a mapping")
        timestamp = data["timestamp"]
        if not isinstance(timestamp, str):
            raise InvalidQueryError("timestamp must be an ISO-8601 string")
        try:
            instant = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError as error:
            raise InvalidQueryError("timestamp must be valid ISO-8601") from error
        return cls(
            query_id=data["query_id"],
            effective_filters=tuple(
                _expression_from_dict(item) for item in filters
            ),
            projections=tuple(
                QueryProjection.from_dict(item) for item in projections
            ),
            ordering=tuple(
                QueryOrdering.from_dict(item) for item in ordering
            ),
            pagination=(
                QueryPagination.from_dict(pagination)
                if pagination is not None
                else None
            ),
            estimates=estimates,
            justifications=tuple(reasons),
            timestamp=instant,
        )


__all__ = [
    "DiscoveryQuery",
    "FilterGroup",
    "FilterGroupOperator",
    "QUERY_SCHEMA_VERSION",
    "QueryFilter",
    "QueryOperator",
    "QueryOrdering",
    "QueryOrderingDirection",
    "QueryPagination",
    "QueryPlan",
    "QueryProjection",
]
