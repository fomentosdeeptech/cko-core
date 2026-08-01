"""Immutable and versioned models for infrastructure-neutral discovery."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, fields
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Self

from cko.core.identity import CanonicalId
from cko.core.metadata import UniversalMetadata
from cko.core.models import Asset
from cko.core.utils import ensure_aware, require_non_empty


DISCOVERY_SCHEMA_VERSION = "1.0"


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, float, str, CanonicalId)):
        return value
    if isinstance(value, datetime):
        return ensure_aware(value)
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, nested in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("mapping keys must be non-empty strings")
            frozen[key] = _freeze(nested)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    raise TypeError(f"unsupported discovery metadata: {type(value).__name__}")


def _primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, CanonicalId):
        return str(value)
    if isinstance(value, datetime):
        return ensure_aware(value).isoformat().replace("+00:00", "Z")
    if isinstance(value, UniversalMetadata):
        return {
            "media_type": value.media_type,
            "created_at": _primitive(value.created_at),
            "modified_at": _primitive(value.modified_at),
            "language": value.language,
            "attributes": _primitive(value.attributes),
        }
    if isinstance(value, Asset):
        return value.to_dict()
    if isinstance(value, _VersionedModel):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_primitive(item) for item in value]
    raise TypeError(f"unsupported discovery value: {type(value).__name__}")


def _json_object(payload: str) -> Mapping[str, object]:
    decoded = json.loads(payload)
    if not isinstance(decoded, dict):
        raise ValueError("discovery JSON must contain an object")
    return decoded


class _VersionedModel:
    model_name: ClassVar[str]

    def to_dict(self) -> dict[str, object]:
        """Serialize this value using the canonical Discovery envelope."""
        return {
            "schema_version": DISCOVERY_SCHEMA_VERSION,
            "model": self.model_name,
            **{
                item.name: _primitive(getattr(self, item.name))
                for item in fields(self)
            },
        }

    def to_json(self) -> str:
        """Serialize this value as deterministic JSON."""
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Reconstruct and validate this model from a mapping."""
        restored = discovery_model_from_dict(payload)
        if not isinstance(restored, cls):
            raise ValueError(f"payload does not represent {cls.model_name}")
        return restored

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Reconstruct and validate this model from JSON."""
        return cls.from_dict(_json_object(payload))


@dataclass(frozen=True, slots=True)
class DiscoverySourceId(_VersionedModel):
    """Stable, adapter-neutral identity of a discovery source."""

    model_name: ClassVar[str] = "discovery_source_id"
    value: str

    def __post_init__(self) -> None:
        value = require_non_empty(self.value, "value")
        if any(character.isspace() for character in value):
            raise ValueError("source id cannot contain whitespace")
        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value


class DiscoveryCapability(str, Enum):
    """Declarative capability advertised by a discovery source."""

    LISTING = "listing"
    METADATA_READ = "metadata_read"
    CONTENT_READ = "content_read"
    INCREMENTAL = "incremental"
    PAGINATION = "pagination"
    CHECKPOINTS = "checkpoints"
    CANCELLATION = "cancellation"
    FILTERING = "filtering"
    CONTINUOUS_OBSERVATION = "continuous_observation"


class DiscoveryStatus(str, Enum):
    """Tool-independent state of a Discovery execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class DiscoveryScope(_VersionedModel):
    """Logical scope understood by a provider, never an OS-bound path."""

    model_name: ClassVar[str] = "discovery_scope"
    reference: str
    attributes: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "reference",
            require_non_empty(self.reference, "reference"),
        )
        object.__setattr__(self, "attributes", _freeze(self.attributes))


@dataclass(frozen=True, slots=True)
class DiscoveryPolicy(_VersionedModel):
    """Neutral limits and include/exclude rules for Discovery."""

    model_name: ClassVar[str] = "discovery_policy"
    include_patterns: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()
    max_items: int | None = None
    page_size: int | None = None
    timeout_seconds: float | None = None
    continue_on_error: bool = False

    def __post_init__(self) -> None:
        for name in ("include_patterns", "exclude_patterns"):
            values = tuple(
                require_non_empty(value, name) for value in getattr(self, name)
            )
            if any(_looks_absolute(value) for value in values):
                raise ValueError(f"{name} cannot contain absolute paths")
            object.__setattr__(self, name, values)
        for name in ("max_items", "page_size", "timeout_seconds"):
            value = getattr(self, name)
            if value is not None and (isinstance(value, bool) or value <= 0):
                raise ValueError(f"{name} must be greater than zero")


@dataclass(frozen=True, slots=True)
class DiscoveryContext(_VersionedModel):
    """Correlation and call context supplied to a Discovery execution."""

    model_name: ClassVar[str] = "discovery_context"
    correlation_id: str
    requested_at: datetime
    actor: str | None = None
    attributes: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "correlation_id",
            require_non_empty(self.correlation_id, "correlation_id"),
        )
        object.__setattr__(self, "requested_at", ensure_aware(self.requested_at))
        if self.actor is not None:
            object.__setattr__(self, "actor", require_non_empty(self.actor, "actor"))
        object.__setattr__(self, "attributes", _freeze(self.attributes))


@dataclass(frozen=True, slots=True)
class DiscoveryRequest(_VersionedModel):
    """Canonical request passed to a DiscoveryProvider."""

    model_name: ClassVar[str] = "discovery_request"
    id: CanonicalId
    source_id: DiscoverySourceId
    scope: DiscoveryScope
    policy: DiscoveryPolicy
    context: DiscoveryContext
    required_capabilities: tuple[DiscoveryCapability, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.id, CanonicalId):
            raise TypeError("id must be CanonicalId")
        if not isinstance(self.source_id, DiscoverySourceId):
            raise TypeError("source_id must be DiscoverySourceId")
        if not isinstance(self.scope, DiscoveryScope):
            raise TypeError("scope must be DiscoveryScope")
        if not isinstance(self.policy, DiscoveryPolicy):
            raise TypeError("policy must be DiscoveryPolicy")
        if not isinstance(self.context, DiscoveryContext):
            raise TypeError("context must be DiscoveryContext")
        capabilities = tuple(
            DiscoveryCapability(value) for value in self.required_capabilities
        )
        if len(set(capabilities)) != len(capabilities):
            raise ValueError("required_capabilities cannot contain duplicates")
        object.__setattr__(self, "required_capabilities", capabilities)


@dataclass(frozen=True, slots=True)
class DiscoveryEvidence(_VersionedModel):
    """Technical evidence supporting an observation."""

    model_name: ClassVar[str] = "discovery_evidence"
    method: str
    observed_at: datetime
    confidence: float | None = None
    attributes: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "method", require_non_empty(self.method, "method"))
        object.__setattr__(self, "observed_at", ensure_aware(self.observed_at))
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        object.__setattr__(self, "attributes", _freeze(self.attributes))


@dataclass(frozen=True, slots=True)
class DiscoveryWarning(_VersionedModel):
    """Non-fatal issue observed during Discovery."""

    model_name: ClassVar[str] = "discovery_warning"
    code: str
    message: str
    item_reference: str | None = None
    details: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", require_non_empty(self.code, "code"))
        object.__setattr__(self, "message", require_non_empty(self.message, "message"))
        if self.item_reference is not None:
            object.__setattr__(
                self,
                "item_reference",
                require_non_empty(self.item_reference, "item_reference"),
            )
        object.__setattr__(self, "details", _freeze(self.details))


@dataclass(frozen=True, slots=True)
class DiscoveryErrorRecord(_VersionedModel):
    """Serializable error record produced without exposing an exception."""

    model_name: ClassVar[str] = "discovery_error_record"
    code: str
    message: str
    recoverable: bool = False
    item_reference: str | None = None
    details: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", require_non_empty(self.code, "code"))
        object.__setattr__(self, "message", require_non_empty(self.message, "message"))
        if self.item_reference is not None:
            object.__setattr__(
                self,
                "item_reference",
                require_non_empty(self.item_reference, "item_reference"),
            )
        object.__setattr__(self, "details", _freeze(self.details))


@dataclass(frozen=True, slots=True)
class DiscoveredItem(_VersionedModel):
    """Observation that is not an official Asset until explicitly mapped."""

    model_name: ClassVar[str] = "discovered_item"
    source_id: DiscoverySourceId
    external_reference: str
    observed_at: datetime
    observation_method: str
    correlation_id: str
    metadata: UniversalMetadata
    evidence: tuple[DiscoveryEvidence, ...] = ()
    confidence: float | None = None
    adapter_version: str | None = None
    canonical_id: CanonicalId | None = None
    attributes: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, DiscoverySourceId):
            raise TypeError("source_id must be DiscoverySourceId")
        object.__setattr__(
            self,
            "external_reference",
            require_non_empty(self.external_reference, "external_reference"),
        )
        object.__setattr__(self, "observed_at", ensure_aware(self.observed_at))
        object.__setattr__(
            self,
            "observation_method",
            require_non_empty(self.observation_method, "observation_method"),
        )
        object.__setattr__(
            self,
            "correlation_id",
            require_non_empty(self.correlation_id, "correlation_id"),
        )
        if not isinstance(self.metadata, UniversalMetadata):
            raise TypeError("metadata must be UniversalMetadata")
        object.__setattr__(
            self,
            "metadata",
            UniversalMetadata(
                media_type=self.metadata.media_type,
                created_at=self.metadata.created_at,
                modified_at=self.metadata.modified_at,
                language=self.metadata.language,
                attributes=_freeze(self.metadata.attributes),
            ),
        )
        evidence = tuple(self.evidence)
        if any(not isinstance(item, DiscoveryEvidence) for item in evidence):
            raise TypeError("evidence must contain DiscoveryEvidence values")
        object.__setattr__(self, "evidence", evidence)
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.adapter_version is not None:
            object.__setattr__(
                self,
                "adapter_version",
                require_non_empty(self.adapter_version, "adapter_version"),
            )
        if self.canonical_id is not None and not isinstance(
            self.canonical_id,
            CanonicalId,
        ):
            raise TypeError("canonical_id must be CanonicalId when provided")
        object.__setattr__(self, "attributes", _freeze(self.attributes))


@dataclass(frozen=True, slots=True)
class DiscoveryMetrics(_VersionedModel):
    """Deterministic counters and timestamps for one execution."""

    model_name: ClassVar[str] = "discovery_metrics"
    observed_count: int
    accepted_count: int
    rejected_count: int
    warning_count: int
    error_count: int
    started_at: datetime
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        for name in (
            "observed_count",
            "accepted_count",
            "rejected_count",
            "warning_count",
            "error_count",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.accepted_count + self.rejected_count > self.observed_count:
            raise ValueError("accepted and rejected counts exceed observed_count")
        started_at = ensure_aware(self.started_at)
        object.__setattr__(self, "started_at", started_at)
        if self.completed_at is not None:
            completed_at = ensure_aware(self.completed_at)
            if completed_at < started_at:
                raise ValueError("completed_at cannot precede started_at")
            object.__setattr__(self, "completed_at", completed_at)


@dataclass(frozen=True, slots=True)
class DiscoveryBatch(_VersionedModel):
    """Immutable page or logical group returned by a provider."""

    model_name: ClassVar[str] = "discovery_batch"
    id: CanonicalId
    sequence: int
    items: tuple[DiscoveredItem, ...] = ()
    warnings: tuple[DiscoveryWarning, ...] = ()
    errors: tuple[DiscoveryErrorRecord, ...] = ()
    final: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.id, CanonicalId):
            raise TypeError("id must be CanonicalId")
        if isinstance(self.sequence, bool) or self.sequence < 0:
            raise ValueError("sequence cannot be negative")
        for name, expected in (
            ("items", DiscoveredItem),
            ("warnings", DiscoveryWarning),
            ("errors", DiscoveryErrorRecord),
        ):
            values = tuple(getattr(self, name))
            if any(not isinstance(value, expected) for value in values):
                raise TypeError(f"{name} contains an invalid value")
            object.__setattr__(self, name, values)


@dataclass(frozen=True, slots=True)
class DiscoveryResult(_VersionedModel):
    """Complete immutable output of one Discovery execution."""

    model_name: ClassVar[str] = "discovery_result"
    request_id: CanonicalId
    source_id: DiscoverySourceId
    status: DiscoveryStatus
    items: tuple[DiscoveredItem, ...]
    warnings: tuple[DiscoveryWarning, ...]
    errors: tuple[DiscoveryErrorRecord, ...]
    metrics: DiscoveryMetrics
    batches: tuple[DiscoveryBatch, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, CanonicalId):
            raise TypeError("request_id must be CanonicalId")
        if not isinstance(self.source_id, DiscoverySourceId):
            raise TypeError("source_id must be DiscoverySourceId")
        object.__setattr__(self, "status", DiscoveryStatus(self.status))
        for name, expected in (
            ("items", DiscoveredItem),
            ("warnings", DiscoveryWarning),
            ("errors", DiscoveryErrorRecord),
            ("batches", DiscoveryBatch),
        ):
            values = tuple(getattr(self, name))
            if any(not isinstance(value, expected) for value in values):
                raise TypeError(f"{name} contains an invalid value")
            object.__setattr__(self, name, values)
        if not isinstance(self.metrics, DiscoveryMetrics):
            raise TypeError("metrics must be DiscoveryMetrics")


def _expect(payload: Mapping[str, object], model: str, names: set[str]) -> None:
    if payload.get("schema_version") != DISCOVERY_SCHEMA_VERSION:
        raise ValueError("unsupported discovery schema_version")
    if payload.get("model") != model:
        raise ValueError(f"payload must represent {model}")
    unknown = set(payload) - {"schema_version", "model"} - names
    if unknown:
        raise ValueError(f"unknown discovery fields: {sorted(unknown)}")
    missing = names - set(payload)
    if missing:
        raise ValueError(f"missing discovery fields: {sorted(missing)}")


def _looks_absolute(value: str) -> bool:
    normalized = value.replace("\\", "/")
    return (
        normalized.startswith("/")
        or normalized.startswith("//")
        or (len(normalized) >= 3 and normalized[1:3] == ":/")
    )


def _dt(value: object, name: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be an ISO 8601 datetime")
    return ensure_aware(datetime.fromisoformat(value.replace("Z", "+00:00")))


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def _sequence(value: object, name: str) -> tuple[object, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    return tuple(value)


def _nested(value: object, expected: type[_VersionedModel]) -> _VersionedModel:
    restored = discovery_model_from_dict(_mapping(value, expected.model_name))
    if not isinstance(restored, expected):
        raise ValueError(f"nested model must be {expected.model_name}")
    return restored


def _metadata(value: object) -> UniversalMetadata:
    payload = _mapping(value, "metadata")
    expected = {"media_type", "created_at", "modified_at", "language", "attributes"}
    if set(payload) != expected:
        raise ValueError("metadata fields are incomplete or unknown")
    return UniversalMetadata(
        media_type=str(payload["media_type"]),
        created_at=_dt(payload["created_at"], "metadata.created_at"),
        modified_at=_dt(payload["modified_at"], "metadata.modified_at"),
        language=None if payload["language"] is None else str(payload["language"]),
        attributes=_mapping(payload["attributes"], "metadata.attributes"),
    )


def discovery_model_from_dict(payload: Mapping[str, object]) -> _VersionedModel:
    """Restore any public Discovery model from its versioned envelope."""
    model = payload.get("model")
    if not isinstance(model, str):
        raise ValueError("discovery model is required")
    names_by_model = {
        "discovery_source_id": {"value"},
        "discovery_scope": {"reference", "attributes"},
        "discovery_policy": {
            "include_patterns", "exclude_patterns", "max_items", "page_size",
            "timeout_seconds", "continue_on_error",
        },
        "discovery_context": {"correlation_id", "requested_at", "actor", "attributes"},
        "discovery_request": {
            "id", "source_id", "scope", "policy", "context", "required_capabilities",
        },
        "discovery_evidence": {"method", "observed_at", "confidence", "attributes"},
        "discovery_warning": {"code", "message", "item_reference", "details"},
        "discovery_error_record": {
            "code", "message", "recoverable", "item_reference", "details",
        },
        "discovered_item": {
            "source_id", "external_reference", "observed_at", "observation_method",
            "correlation_id", "metadata", "evidence", "confidence",
            "adapter_version", "canonical_id", "attributes",
        },
        "discovery_metrics": {
            "observed_count", "accepted_count", "rejected_count", "warning_count",
            "error_count", "started_at", "completed_at",
        },
        "discovery_batch": {"id", "sequence", "items", "warnings", "errors", "final"},
        "discovery_result": {
            "request_id", "source_id", "status", "items", "warnings", "errors",
            "metrics", "batches",
        },
    }
    if model not in names_by_model:
        raise ValueError(f"unknown discovery model: {model}")
    _expect(payload, model, names_by_model[model])
    if model == "discovery_source_id":
        return DiscoverySourceId(str(payload["value"]))
    if model == "discovery_scope":
        return DiscoveryScope(
            str(payload["reference"]),
            _mapping(payload["attributes"], "attributes"),
        )
    if model == "discovery_policy":
        return DiscoveryPolicy(
            tuple(
                str(value)
                for value in _sequence(payload["include_patterns"], "include_patterns")
            ),
            tuple(
                str(value)
                for value in _sequence(payload["exclude_patterns"], "exclude_patterns")
            ),
            payload["max_items"], payload["page_size"], payload["timeout_seconds"],
            bool(payload["continue_on_error"]),
        )
    if model == "discovery_context":
        return DiscoveryContext(
            str(payload["correlation_id"]),
            _dt(payload["requested_at"], "requested_at"),
            None if payload["actor"] is None else str(payload["actor"]),
            _mapping(payload["attributes"], "attributes"),
        )
    if model == "discovery_request":
        return DiscoveryRequest(
            CanonicalId.parse(str(payload["id"])),
            _nested(payload["source_id"], DiscoverySourceId),
            _nested(payload["scope"], DiscoveryScope),
            _nested(payload["policy"], DiscoveryPolicy),
            _nested(payload["context"], DiscoveryContext),
            tuple(DiscoveryCapability(value) for value in _sequence(
                payload["required_capabilities"], "required_capabilities"
            )),
        )
    if model == "discovery_evidence":
        return DiscoveryEvidence(
            str(payload["method"]), _dt(payload["observed_at"], "observed_at"),
            payload["confidence"], _mapping(payload["attributes"], "attributes"),
        )
    if model == "discovery_warning":
        return DiscoveryWarning(
            str(payload["code"]), str(payload["message"]),
            None
            if payload["item_reference"] is None
            else str(payload["item_reference"]),
            _mapping(payload["details"], "details"),
        )
    if model == "discovery_error_record":
        return DiscoveryErrorRecord(
            str(payload["code"]), str(payload["message"]), bool(payload["recoverable"]),
            None
            if payload["item_reference"] is None
            else str(payload["item_reference"]),
            _mapping(payload["details"], "details"),
        )
    if model == "discovered_item":
        return DiscoveredItem(
            _nested(payload["source_id"], DiscoverySourceId),
            str(payload["external_reference"]),
            _dt(payload["observed_at"], "observed_at"),
            str(payload["observation_method"]), str(payload["correlation_id"]),
            _metadata(payload["metadata"]),
            tuple(
                _nested(value, DiscoveryEvidence)
                for value in _sequence(payload["evidence"], "evidence")
            ),
            payload["confidence"],
            None
            if payload["adapter_version"] is None
            else str(payload["adapter_version"]),
            None
            if payload["canonical_id"] is None
            else CanonicalId.parse(str(payload["canonical_id"])),
            _mapping(payload["attributes"], "attributes"),
        )
    if model == "discovery_metrics":
        return DiscoveryMetrics(
            int(payload["observed_count"]), int(payload["accepted_count"]),
            int(payload["rejected_count"]), int(payload["warning_count"]),
            int(payload["error_count"]), _dt(payload["started_at"], "started_at"),
            None
            if payload["completed_at"] is None
            else _dt(payload["completed_at"], "completed_at"),
        )
    if model == "discovery_batch":
        return DiscoveryBatch(
            CanonicalId.parse(str(payload["id"])), int(payload["sequence"]),
            tuple(
                _nested(value, DiscoveredItem)
                for value in _sequence(payload["items"], "items")
            ),
            tuple(
                _nested(value, DiscoveryWarning)
                for value in _sequence(payload["warnings"], "warnings")
            ),
            tuple(
                _nested(value, DiscoveryErrorRecord)
                for value in _sequence(payload["errors"], "errors")
            ),
            bool(payload["final"]),
        )
    return DiscoveryResult(
        CanonicalId.parse(str(payload["request_id"])),
        _nested(payload["source_id"], DiscoverySourceId),
        DiscoveryStatus(str(payload["status"])),
        tuple(
            _nested(value, DiscoveredItem)
            for value in _sequence(payload["items"], "items")
        ),
        tuple(
            _nested(value, DiscoveryWarning)
            for value in _sequence(payload["warnings"], "warnings")
        ),
        tuple(
            _nested(value, DiscoveryErrorRecord)
            for value in _sequence(payload["errors"], "errors")
        ),
        _nested(payload["metrics"], DiscoveryMetrics),
        tuple(
            _nested(value, DiscoveryBatch)
            for value in _sequence(payload["batches"], "batches")
        ),
    )


__all__ = [
    "DISCOVERY_SCHEMA_VERSION", "DiscoveredItem", "DiscoveryBatch",
    "DiscoveryCapability", "DiscoveryContext", "DiscoveryErrorRecord",
    "DiscoveryEvidence", "DiscoveryMetrics", "DiscoveryPolicy", "DiscoveryRequest",
    "DiscoveryResult", "DiscoveryScope", "DiscoverySourceId", "DiscoveryStatus",
    "DiscoveryWarning", "discovery_model_from_dict",
]
