"""Immutable and strictly serializable models for query evaluation."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Self

from cko.core.identity import CanonicalId
from cko.core.utils import utc_now

from .cancellation import CancellationToken
from .query_evaluation_errors import InvalidQueryEvaluationPolicyError
from .query_models import QueryPlan


QUERY_EVALUATION_SCHEMA_VERSION = "1.0"


class MissingAttributeBehavior(str, Enum):
    """Policy outcomes for a missing attribute used by a predicate."""

    NO_MATCH = "no_match"
    ERROR = "error"


class IncompatibleTypeBehavior(str, Enum):
    """Policy outcomes for an unsafe comparison between incompatible types."""

    NO_MATCH = "no_match"
    ERROR = "error"


class EvaluationErrorBehavior(str, Enum):
    """Policy outcomes for a controlled evaluation failure."""

    RAISE = "raise"
    RECORD = "record"


class OrderingValuePosition(str, Enum):
    """Stable position assigned to missing or null ordering values."""

    FIRST = "first"
    LAST = "last"


def _non_empty(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _aware(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str, CanonicalId)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("evaluation values must contain finite numbers")
        return value
    if isinstance(value, datetime):
        return _aware(value)
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, nested in value.items():
            normalized = _non_empty(key, "mapping key")
            frozen[normalized] = _freeze(nested)
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    raise TypeError(f"unsupported evaluation value: {type(value).__name__}")


def _primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, CanonicalId):
        return str(value)
    if isinstance(value, datetime):
        return _aware(value).isoformat().replace("+00:00", "Z")
    if isinstance(value, QueryPlan):
        return value.to_dict()
    if isinstance(value, CancellationToken):
        return {
            "id": str(value.id),
            "is_cancelled": value.is_cancelled,
            "reason": value.reason,
        }
    if isinstance(value, _EvaluationModel):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_primitive(item) for item in value]
    raise TypeError(f"unsupported serialization value: {type(value).__name__}")


def _instant(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO-8601 string")
    try:
        return _aware(datetime.fromisoformat(value.replace("Z", "+00:00")))
    except ValueError as error:
        raise ValueError("timestamp must be valid ISO-8601") from error


def _envelope(
    payload: Mapping[str, object], model: str, names: tuple[str, ...]
) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise ValueError(f"{model} payload must be a mapping")
    expected = {"schema_version", "model", *names}
    actual = set(payload)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        detail = f"missing={missing}; unknown={unknown}"
        raise ValueError(f"invalid {model} envelope ({detail})")
    if payload["schema_version"] != QUERY_EVALUATION_SCHEMA_VERSION:
        raise ValueError("unsupported query evaluation schema version")
    if payload["model"] != model:
        raise ValueError(f"payload does not represent {model}")
    return {name: payload[name] for name in names}


def _array(value: object, name: str) -> tuple[object, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a JSON array")
    return tuple(value)


def _mapping_array(value: object, name: str) -> tuple[Mapping[str, object], ...]:
    declared = _array(value, name)
    if any(not isinstance(item, Mapping) for item in declared):
        raise ValueError(f"{name} must contain JSON objects")
    return declared


class _EvaluationModel:
    model_name: ClassVar[str]
    schema_version: ClassVar[str] = QUERY_EVALUATION_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """Serialize with the strict canonical evaluation envelope."""
        return {
            "schema_version": self.schema_version,
            "model": self.model_name,
            **{
                item.name: _primitive(getattr(self, item.name))
                for item in fields(self)
            },
        }

    def to_json(self) -> str:
        """Serialize as deterministic UTF-8-compatible JSON."""
        return json.dumps(
            self.to_dict(),
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize from one strict JSON object."""
        try:
            decoded = json.loads(payload)
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError("evaluation JSON is invalid") from error
        if not isinstance(decoded, dict):
            raise ValueError("evaluation JSON must contain an object")
        return cls.from_dict(decoded)


@dataclass(frozen=True, slots=True)
class QueryEvaluationPolicy(_EvaluationModel):
    """Versioned immutable safety policy for in-memory evaluation."""

    model_name: ClassVar[str] = "query_evaluation_policy"
    missing_attribute: MissingAttributeBehavior = MissingAttributeBehavior.NO_MATCH
    incompatible_type: IncompatibleTypeBehavior = IncompatibleTypeBehavior.ERROR
    evaluation_error: EvaluationErrorBehavior = EvaluationErrorBehavior.RAISE
    missing_ordering_position: OrderingValuePosition = OrderingValuePosition.LAST
    none_ordering_position: OrderingValuePosition = OrderingValuePosition.LAST
    require_logical_identity: bool = True
    max_subjects: int = 10_000
    allow_partial_evaluation: bool = False

    def __post_init__(self) -> None:
        try:
            object.__setattr__(
                self, "missing_attribute", MissingAttributeBehavior(self.missing_attribute)
            )
            object.__setattr__(
                self, "incompatible_type", IncompatibleTypeBehavior(self.incompatible_type)
            )
            object.__setattr__(
                self, "evaluation_error", EvaluationErrorBehavior(self.evaluation_error)
            )
            object.__setattr__(
                self,
                "missing_ordering_position",
                OrderingValuePosition(self.missing_ordering_position),
            )
            object.__setattr__(
                self,
                "none_ordering_position",
                OrderingValuePosition(self.none_ordering_position),
            )
        except (TypeError, ValueError) as error:
            raise InvalidQueryEvaluationPolicyError(
                "query evaluation policy contains an unsupported behavior"
            ) from error
        if (
            isinstance(self.max_subjects, bool)
            or not isinstance(self.max_subjects, int)
            or self.max_subjects < 1
        ):
            raise InvalidQueryEvaluationPolicyError(
                "max_subjects must be a positive integer"
            )
        if not isinstance(self.require_logical_identity, bool) or not isinstance(
            self.allow_partial_evaluation, bool
        ):
            raise InvalidQueryEvaluationPolicyError(
                "policy flags must be boolean values"
            )
        if (
            self.evaluation_error is EvaluationErrorBehavior.RECORD
            and not self.allow_partial_evaluation
        ):
            raise InvalidQueryEvaluationPolicyError(
                "recording errors requires partial evaluation permission"
            )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a policy from a strict mapping."""
        names = tuple(item.name for item in fields(cls))
        return cls(**_envelope(payload, cls.model_name, names))


@dataclass(frozen=True, slots=True)
class QueryEvaluationContext(_EvaluationModel):
    """Immutable neutral context shared by one evaluation execution."""

    model_name: ClassVar[str] = "query_evaluation_context"
    correlation_id: str
    actor: str
    timestamp: datetime = field(default_factory=utc_now)
    attributes: Mapping[str, object] = field(default_factory=dict)
    cancellation_token: CancellationToken | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "correlation_id", _non_empty(self.correlation_id, "correlation_id")
        )
        object.__setattr__(self, "actor", _non_empty(self.actor, "actor"))
        object.__setattr__(self, "timestamp", _aware(self.timestamp))
        object.__setattr__(self, "attributes", _freeze(self.attributes))
        if self.cancellation_token is not None and not isinstance(
            self.cancellation_token, CancellationToken
        ):
            raise TypeError("cancellation_token must be CancellationToken")

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize an evaluation context from a strict mapping."""
        names = tuple(item.name for item in fields(cls))
        data = _envelope(payload, cls.model_name, names)
        attributes = data["attributes"]
        if not isinstance(attributes, Mapping):
            raise ValueError("attributes must be a mapping")
        token_data = data["cancellation_token"]
        token: CancellationToken | None = None
        if token_data is not None:
            if not isinstance(token_data, Mapping) or set(token_data) != {
                "id", "is_cancelled", "reason"
            }:
                raise ValueError("cancellation_token is invalid")
            if not isinstance(token_data["is_cancelled"], bool):
                raise ValueError("cancellation_token state must be boolean")
            token = CancellationToken(CanonicalId.parse(str(token_data["id"])))
            if token_data["is_cancelled"]:
                token.cancel(str(token_data["reason"] or "cancellation requested"))
        return cls(
            correlation_id=data["correlation_id"],
            actor=data["actor"],
            timestamp=_instant(data["timestamp"]),
            attributes=attributes,
            cancellation_token=token,
        )


@dataclass(frozen=True, slots=True)
class PredicateEvaluationRecord(_EvaluationModel):
    """Immutable audit record for one evaluated atomic predicate."""

    model_name: ClassVar[str] = "predicate_evaluation_record"
    attribute: str
    operator: str
    expected_value: object
    observed_value: object
    matched: bool
    attribute_exists: bool
    justification: str
    code: str
    logical_path: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("attribute", "operator", "justification", "code"):
            object.__setattr__(self, name, _non_empty(getattr(self, name), name))
        object.__setattr__(self, "expected_value", _freeze(self.expected_value))
        object.__setattr__(self, "observed_value", _freeze(self.observed_value))
        object.__setattr__(
            self,
            "logical_path",
            tuple(_non_empty(item, "logical_path item") for item in self.logical_path),
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a predicate record from a strict mapping."""
        names = tuple(item.name for item in fields(cls))
        data = _envelope(payload, cls.model_name, names)
        data["logical_path"] = _array(data["logical_path"], "logical_path")
        return cls(**data)


@dataclass(frozen=True, slots=True)
class QueryMatchResult(_EvaluationModel):
    """Versioned audit summary for one subject's filter decision."""

    model_name: ClassVar[str] = "query_match_result"
    logical_identity: str
    matched: bool
    evaluated_filters: int
    approved_filters: int
    rejected_filters: int
    missing_attributes: tuple[str, ...]
    controlled_errors: tuple[str, ...]
    justifications: tuple[str, ...]
    predicate_records: tuple[PredicateEvaluationRecord, ...]
    timestamp: datetime

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "logical_identity", _non_empty(self.logical_identity, "logical_identity")
        )
        records = tuple(self.predicate_records)
        if any(not isinstance(item, PredicateEvaluationRecord) for item in records):
            raise TypeError("predicate_records must contain canonical records")
        if self.evaluated_filters != len(records):
            raise ValueError("evaluated_filters must equal predicate record count")
        if self.approved_filters + self.rejected_filters != len(records):
            raise ValueError("approved and rejected filter counts are inconsistent")
        object.__setattr__(self, "predicate_records", records)
        object.__setattr__(self, "missing_attributes", tuple(self.missing_attributes))
        object.__setattr__(self, "controlled_errors", tuple(self.controlled_errors))
        object.__setattr__(self, "justifications", tuple(self.justifications))
        object.__setattr__(self, "timestamp", _aware(self.timestamp))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize one subject match result from a strict mapping."""
        names = tuple(item.name for item in fields(cls))
        data = _envelope(payload, cls.model_name, names)
        for name in ("missing_attributes", "controlled_errors", "justifications"):
            data[name] = _array(data[name], name)
        data["predicate_records"] = tuple(
            PredicateEvaluationRecord.from_dict(item)
            for item in _mapping_array(
                data["predicate_records"], "predicate_records"
            )
        )
        data["timestamp"] = _instant(data["timestamp"])
        return cls(**data)


@dataclass(frozen=True, slots=True)
class ProjectedQueryItem(_EvaluationModel):
    """Immutable explicit projection of an approved subject."""

    model_name: ClassVar[str] = "projected_query_item"
    logical_identity: str
    attributes: Mapping[str, object]
    missing_attributes: tuple[str, ...]
    evaluation_metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "logical_identity", _non_empty(self.logical_identity, "logical_identity")
        )
        object.__setattr__(self, "attributes", _freeze(self.attributes))
        object.__setattr__(self, "missing_attributes", tuple(self.missing_attributes))
        object.__setattr__(
            self, "evaluation_metadata", _freeze(self.evaluation_metadata)
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a projected item from a strict mapping."""
        names = tuple(item.name for item in fields(cls))
        data = _envelope(payload, cls.model_name, names)
        if not isinstance(data["attributes"], Mapping) or not isinstance(
            data["evaluation_metadata"], Mapping
        ):
            raise ValueError("projected item mappings are invalid")
        data["missing_attributes"] = _array(
            data["missing_attributes"], "missing_attributes"
        )
        return cls(**data)


@dataclass(frozen=True, slots=True)
class QueryEvaluationResult(_EvaluationModel):
    """Complete immutable and auditable outcome of query evaluation."""

    model_name: ClassVar[str] = "query_evaluation_result"
    query_id: str
    plan: QueryPlan
    matched_items: tuple[str, ...]
    projected_items: tuple[ProjectedQueryItem, ...]
    evaluation_records: tuple[QueryMatchResult, ...]
    total_received: int
    total_evaluated: int
    total_matched: int
    total_rejected: int
    total_returned: int
    applied_offset: int
    applied_limit: int | None
    warnings: tuple[str, ...]
    controlled_errors: tuple[str, ...]
    timestamp: datetime
    logical_duration: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "query_id", _non_empty(self.query_id, "query_id"))
        if not isinstance(self.plan, QueryPlan) or self.plan.query_id != self.query_id:
            raise ValueError("plan must represent query_id")
        object.__setattr__(self, "matched_items", tuple(self.matched_items))
        object.__setattr__(self, "projected_items", tuple(self.projected_items))
        object.__setattr__(self, "evaluation_records", tuple(self.evaluation_records))
        object.__setattr__(self, "warnings", tuple(self.warnings))
        object.__setattr__(self, "controlled_errors", tuple(self.controlled_errors))
        object.__setattr__(self, "timestamp", _aware(self.timestamp))
        if self.total_evaluated != len(self.evaluation_records):
            raise ValueError("total_evaluated is inconsistent")
        if self.total_matched + self.total_rejected != self.total_evaluated:
            raise ValueError("match totals are inconsistent")
        if self.total_returned != len(self.matched_items):
            raise ValueError("total_returned is inconsistent")

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a complete evaluation result from a strict mapping."""
        names = tuple(item.name for item in fields(cls))
        data = _envelope(payload, cls.model_name, names)
        plan = data["plan"]
        if not isinstance(plan, Mapping):
            raise ValueError("plan must be a mapping")
        data["plan"] = QueryPlan.from_dict(plan)
        for name in ("matched_items", "warnings", "controlled_errors"):
            data[name] = _array(data[name], name)
        data["projected_items"] = tuple(
            ProjectedQueryItem.from_dict(item)
            for item in _mapping_array(data["projected_items"], "projected_items")
        )
        data["evaluation_records"] = tuple(
            QueryMatchResult.from_dict(item)
            for item in _mapping_array(
                data["evaluation_records"], "evaluation_records"
            )
        )
        data["timestamp"] = _instant(data["timestamp"])
        return cls(**data)


__all__ = [
    "EvaluationErrorBehavior",
    "IncompatibleTypeBehavior",
    "MissingAttributeBehavior",
    "OrderingValuePosition",
    "PredicateEvaluationRecord",
    "ProjectedQueryItem",
    "QUERY_EVALUATION_SCHEMA_VERSION",
    "QueryEvaluationContext",
    "QueryEvaluationPolicy",
    "QueryEvaluationResult",
    "QueryMatchResult",
]
