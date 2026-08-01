"""Immutable and versioned models for Discovery capabilities."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Iterable, Mapping, Self, Sequence

from cko.core.identity import SemanticVersion
from cko.core.utils import ensure_aware, require_non_empty

from .capability_errors import InvalidCapabilityError


CAPABILITY_SCHEMA_VERSION = "1.0"


def _freeze(value: object) -> object:
    """Validate and freeze a JSON-compatible value."""
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidCapabilityError("metadata numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, nested in value.items():
            if not isinstance(key, str) or not key.strip():
                raise InvalidCapabilityError(
                    "metadata keys must be non-empty strings"
                )
            frozen[key] = _freeze(nested)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    raise InvalidCapabilityError(
        f"unsupported metadata value: {type(value).__name__}"
    )


def _primitive(value: object) -> object:
    """Convert frozen values into deterministic JSON primitives."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, tuple):
        return [_primitive(item) for item in value]
    raise InvalidCapabilityError(
        f"unsupported serialized value: {type(value).__name__}"
    )


def _json(payload: Mapping[str, object]) -> str:
    """Return canonical JSON for a public capability envelope."""
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _object(payload: str) -> Mapping[str, object]:
    """Decode a JSON object or raise the public model error."""
    try:
        decoded = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as error:
        raise InvalidCapabilityError("capability JSON is invalid") from error
    if not isinstance(decoded, dict):
        raise InvalidCapabilityError("capability JSON must contain an object")
    return decoded


def _strict(
    payload: Mapping[str, object], expected: set[str], model: str
) -> None:
    """Reject unknown, missing or unsupported public envelope fields."""
    unknown = set(payload) - expected
    missing = expected - set(payload)
    if unknown:
        raise InvalidCapabilityError(
            f"unknown {model} fields: {sorted(unknown)}"
        )
    if missing:
        raise InvalidCapabilityError(
            f"missing {model} fields: {sorted(missing)}"
        )
    if payload.get("schema_version") != CAPABILITY_SCHEMA_VERSION:
        raise InvalidCapabilityError(
            f"unsupported {model} schema_version"
        )


def _version(value: object, field_name: str) -> SemanticVersion:
    """Parse a semantic version from a strict string field."""
    if not isinstance(value, str):
        raise InvalidCapabilityError(f"{field_name} must be a string")
    try:
        return SemanticVersion.parse(value)
    except ValueError as error:
        raise InvalidCapabilityError(f"{field_name} is invalid") from error


class CapabilityCategory(str, Enum):
    """Canonical public categories for Discovery capabilities."""

    DISCOVERY = "discovery"
    INGESTION = "ingestion"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    EXECUTION = "execution"
    DELIVERY = "delivery"
    OBSERVABILITY = "observability"
    SECURITY = "security"
    EXTENSION = "extension"


class CapabilityRequirementType(str, Enum):
    """Supported requirement semantics."""

    REQUIRED = "required"
    OPTIONAL = "optional"
    PROHIBITED = "prohibited"


@dataclass(frozen=True, slots=True)
class CapabilityRequirement:
    """Immutable version-aware requirement for one capability identity."""

    capability_id: str
    requirement_type: CapabilityRequirementType
    minimum_version: SemanticVersion | None = None
    incompatible_versions: Sequence[SemanticVersion] = ()
    reason: str | None = None
    schema_version: str = CAPABILITY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        """Normalize identity, enum, versions and optional rationale."""
        try:
            capability_id = require_non_empty(
                self.capability_id, "capability_id"
            )
            requirement_type = CapabilityRequirementType(
                self.requirement_type
            )
        except (TypeError, ValueError) as error:
            raise InvalidCapabilityError(str(error)) from error
        if self.schema_version != CAPABILITY_SCHEMA_VERSION:
            raise InvalidCapabilityError(
                "unsupported requirement schema_version"
            )
        if self.minimum_version is not None and not isinstance(
            self.minimum_version, SemanticVersion
        ):
            raise InvalidCapabilityError(
                "minimum_version must be SemanticVersion"
            )
        versions = tuple(self.incompatible_versions)
        if any(not isinstance(item, SemanticVersion) for item in versions):
            raise InvalidCapabilityError(
                "incompatible_versions must contain SemanticVersion"
            )
        versions = tuple(sorted(set(versions)))
        reason = self.reason
        if reason is not None:
            try:
                reason = require_non_empty(reason, "reason")
            except (TypeError, ValueError) as error:
                raise InvalidCapabilityError(str(error)) from error
        object.__setattr__(self, "capability_id", capability_id)
        object.__setattr__(self, "requirement_type", requirement_type)
        object.__setattr__(self, "incompatible_versions", versions)
        object.__setattr__(self, "reason", reason)

    def is_satisfied_by(self, capability: Capability | None) -> bool:
        """Return whether a capability satisfies this requirement."""
        if self.requirement_type is CapabilityRequirementType.PROHIBITED:
            if capability is None:
                return True
            if not self.incompatible_versions:
                return False
            return capability.version not in self.incompatible_versions
        if capability is None:
            return self.requirement_type is CapabilityRequirementType.OPTIONAL
        if capability.id != self.capability_id:
            return False
        if (
            self.minimum_version is not None
            and capability.version < self.minimum_version
        ):
            return False
        return capability.version not in self.incompatible_versions

    def to_dict(self) -> dict[str, object]:
        """Return the strict versioned requirement envelope."""
        return {
            "schema_version": self.schema_version,
            "capability_id": self.capability_id,
            "requirement_type": self.requirement_type.value,
            "minimum_version": (
                str(self.minimum_version)
                if self.minimum_version is not None
                else None
            ),
            "incompatible_versions": [
                str(item) for item in self.incompatible_versions
            ],
            "reason": self.reason,
        }

    def to_json(self) -> str:
        """Serialize the requirement as deterministic JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore a requirement from a strict public mapping."""
        expected = {
            "schema_version",
            "capability_id",
            "requirement_type",
            "minimum_version",
            "incompatible_versions",
            "reason",
        }
        _strict(payload, expected, "requirement")
        versions = payload["incompatible_versions"]
        if not isinstance(versions, list):
            raise InvalidCapabilityError(
                "incompatible_versions must be an array"
            )
        minimum = payload["minimum_version"]
        if minimum is not None:
            minimum = _version(minimum, "minimum_version")
        reason = payload["reason"]
        if reason is not None and not isinstance(reason, str):
            raise InvalidCapabilityError("reason must be a string or null")
        try:
            requirement_type = CapabilityRequirementType(
                payload["requirement_type"]
            )
        except (TypeError, ValueError) as error:
            raise InvalidCapabilityError(
                "requirement_type is invalid"
            ) from error
        return cls(
            str(payload["capability_id"]),
            requirement_type,
            minimum,
            tuple(_version(item, "incompatible_version") for item in versions),
            reason,
            str(payload["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Restore a requirement from deterministic JSON."""
        return cls.from_dict(_object(payload))


@dataclass(frozen=True, slots=True)
class Capability:
    """Canonical immutable declaration of a Discovery capability."""

    id: str
    name: str
    description: str
    category: CapabilityCategory
    version: SemanticVersion
    dependencies: Sequence[CapabilityRequirement] = ()
    incompatibilities: Sequence[CapabilityRequirement] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = CAPABILITY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        """Validate and freeze the complete capability declaration."""
        try:
            capability_id = require_non_empty(self.id, "id")
            name = require_non_empty(self.name, "name")
            description = require_non_empty(self.description, "description")
            category = CapabilityCategory(self.category)
        except (TypeError, ValueError) as error:
            raise InvalidCapabilityError(str(error)) from error
        if not isinstance(self.version, SemanticVersion):
            raise InvalidCapabilityError("version must be SemanticVersion")
        if self.schema_version != CAPABILITY_SCHEMA_VERSION:
            raise InvalidCapabilityError(
                "unsupported capability schema_version"
            )
        dependencies = tuple(self.dependencies)
        incompatibilities = tuple(self.incompatibilities)
        if any(
            not isinstance(item, CapabilityRequirement)
            for item in dependencies + incompatibilities
        ):
            raise InvalidCapabilityError(
                "dependencies and incompatibilities must contain requirements"
            )
        if any(
            item.requirement_type is CapabilityRequirementType.PROHIBITED
            for item in dependencies
        ):
            raise InvalidCapabilityError(
                "dependencies cannot be prohibited requirements"
            )
        if any(
            item.requirement_type is not CapabilityRequirementType.PROHIBITED
            for item in incompatibilities
        ):
            raise InvalidCapabilityError(
                "incompatibilities must be prohibited requirements"
            )
        identifiers = [item.capability_id for item in dependencies]
        identifiers.extend(item.capability_id for item in incompatibilities)
        if self.id in identifiers:
            raise InvalidCapabilityError(
                "a capability cannot depend on or conflict with itself"
            )
        if len(identifiers) != len(set(identifiers)):
            raise InvalidCapabilityError(
                "dependency and incompatibility identities must be unique"
            )
        metadata = _freeze(self.metadata)
        if not isinstance(metadata, Mapping):
            raise InvalidCapabilityError("metadata must be an object")
        object.__setattr__(self, "id", capability_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "category", category)
        object.__setattr__(
            self,
            "dependencies",
            tuple(sorted(dependencies, key=lambda item: item.capability_id)),
        )
        object.__setattr__(
            self,
            "incompatibilities",
            tuple(
                sorted(
                    incompatibilities,
                    key=lambda item: item.capability_id,
                )
            ),
        )
        object.__setattr__(self, "metadata", metadata)

    def to_dict(self) -> dict[str, object]:
        """Return the strict versioned capability envelope."""
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "version": str(self.version),
            "dependencies": [item.to_dict() for item in self.dependencies],
            "incompatibilities": [
                item.to_dict() for item in self.incompatibilities
            ],
            "metadata": _primitive(self.metadata),
        }

    def to_json(self) -> str:
        """Serialize the capability as deterministic JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore a capability while rejecting unknown fields."""
        expected = {
            "schema_version",
            "id",
            "name",
            "description",
            "category",
            "version",
            "dependencies",
            "incompatibilities",
            "metadata",
        }
        _strict(payload, expected, "capability")
        dependencies = payload["dependencies"]
        incompatibilities = payload["incompatibilities"]
        metadata = payload["metadata"]
        if not isinstance(dependencies, list):
            raise InvalidCapabilityError("dependencies must be an array")
        if not isinstance(incompatibilities, list):
            raise InvalidCapabilityError("incompatibilities must be an array")
        if not isinstance(metadata, Mapping):
            raise InvalidCapabilityError("metadata must be an object")
        if any(not isinstance(item, Mapping) for item in dependencies):
            raise InvalidCapabilityError(
                "dependencies must contain objects"
            )
        if any(not isinstance(item, Mapping) for item in incompatibilities):
            raise InvalidCapabilityError(
                "incompatibilities must contain objects"
            )
        try:
            category = CapabilityCategory(payload["category"])
        except (TypeError, ValueError) as error:
            raise InvalidCapabilityError("category is invalid") from error
        return cls(
            str(payload["id"]),
            str(payload["name"]),
            str(payload["description"]),
            category,
            _version(payload["version"], "version"),
            tuple(CapabilityRequirement.from_dict(item) for item in dependencies),
            tuple(
                CapabilityRequirement.from_dict(item)
                for item in incompatibilities
            ),
            metadata,
            str(payload["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Restore a capability from deterministic JSON."""
        return cls.from_dict(_object(payload))


@dataclass(frozen=True, slots=True)
class CapabilitySet:
    """Immutable collection supporting deterministic capability set algebra."""

    capabilities: Sequence[Capability] = ()
    schema_version: str = CAPABILITY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        """Validate unique identities and impose canonical ordering."""
        if self.schema_version != CAPABILITY_SCHEMA_VERSION:
            raise InvalidCapabilityError(
                "unsupported capability set schema_version"
            )
        capabilities = tuple(self.capabilities)
        if any(not isinstance(item, Capability) for item in capabilities):
            raise InvalidCapabilityError(
                "capability set must contain Capability"
            )
        identifiers = [item.id for item in capabilities]
        if len(identifiers) != len(set(identifiers)):
            raise InvalidCapabilityError(
                "capability identities must be unique within a set"
            )
        object.__setattr__(
            self,
            "capabilities",
            tuple(sorted(capabilities, key=lambda item: item.id)),
        )

    @classmethod
    def of(cls, capabilities: Iterable[Capability]) -> Self:
        """Create a capability set from any finite iterable."""
        return cls(tuple(capabilities))

    def __iter__(self):
        """Iterate capabilities in canonical identity order."""
        return iter(self.capabilities)

    def __len__(self) -> int:
        """Return the number of declared capabilities."""
        return len(self.capabilities)

    def __contains__(self, capability_id: object) -> bool:
        """Return whether a capability identity is present."""
        return isinstance(capability_id, str) and self.get(capability_id) is not None

    def get(self, capability_id: str) -> Capability | None:
        """Return a capability by identity, or ``None`` when absent."""
        return next(
            (item for item in self.capabilities if item.id == capability_id),
            None,
        )

    def union(self, other: Self) -> Self:
        """Return a union, rejecting divergent declarations for one identity."""
        self._require_set(other)
        merged = {item.id: item for item in self.capabilities}
        for item in other:
            current = merged.get(item.id)
            if current is not None and current != item:
                raise InvalidCapabilityError(
                    f"conflicting declarations for capability {item.id!r}"
                )
            merged[item.id] = item
        return type(self).of(merged.values())

    def difference(self, other: Self) -> Self:
        """Return capabilities whose identities are absent from ``other``."""
        self._require_set(other)
        return type(self).of(
            item for item in self if other.get(item.id) is None
        )

    def intersection(self, other: Self) -> Self:
        """Return identical declarations present in both sets."""
        self._require_set(other)
        return type(self).of(
            item for item in self if other.get(item.id) == item
        )

    def __or__(self, other: Self) -> Self:
        """Implement the union operator."""
        return self.union(other)

    def __sub__(self, other: Self) -> Self:
        """Implement the difference operator."""
        return self.difference(other)

    def __and__(self, other: Self) -> Self:
        """Implement the intersection operator."""
        return self.intersection(other)

    def __le__(self, other: Self) -> bool:
        """Compare support by identity and minimum semantic version."""
        self._require_set(other)
        return all(
            (candidate := other.get(item.id)) is not None
            and candidate.version >= item.version
            for item in self
        )

    def __lt__(self, other: Self) -> bool:
        """Return strict support-subset ordering."""
        return self <= other and self != other

    def __ge__(self, other: Self) -> bool:
        """Return support-superset ordering."""
        return other <= self

    def __gt__(self, other: Self) -> bool:
        """Return strict support-superset ordering."""
        return other < self

    @staticmethod
    def _require_set(other: object) -> None:
        """Reject algebra operations with unrelated values."""
        if not isinstance(other, CapabilitySet):
            raise TypeError("capability set operation requires CapabilitySet")

    def to_dict(self) -> dict[str, object]:
        """Return the strict versioned set envelope."""
        return {
            "schema_version": self.schema_version,
            "capabilities": [item.to_dict() for item in self.capabilities],
        }

    def to_json(self) -> str:
        """Serialize the set as deterministic JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore a capability set from a strict mapping."""
        _strict(payload, {"schema_version", "capabilities"}, "capability set")
        capabilities = payload["capabilities"]
        if not isinstance(capabilities, list) or any(
            not isinstance(item, Mapping) for item in capabilities
        ):
            raise InvalidCapabilityError(
                "capabilities must be an array of objects"
            )
        return cls(
            tuple(Capability.from_dict(item) for item in capabilities),
            str(payload["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Restore a capability set from deterministic JSON."""
        return cls.from_dict(_object(payload))


@dataclass(frozen=True, slots=True)
class CapabilityReport:
    """Immutable audit report for validation and negotiation outcomes."""

    accepted: CapabilitySet
    rejected: CapabilitySet
    missing: Sequence[CapabilityRequirement]
    conflicting: CapabilitySet
    justifications: Mapping[str, Sequence[str]]
    timestamp: datetime
    schema_version: str = CAPABILITY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        """Validate and freeze all audit-report fields."""
        for name in ("accepted", "rejected", "conflicting"):
            if not isinstance(getattr(self, name), CapabilitySet):
                raise InvalidCapabilityError(f"{name} must be CapabilitySet")
        missing = tuple(self.missing)
        if any(not isinstance(item, CapabilityRequirement) for item in missing):
            raise InvalidCapabilityError(
                "missing must contain CapabilityRequirement"
            )
        if self.schema_version != CAPABILITY_SCHEMA_VERSION:
            raise InvalidCapabilityError(
                "unsupported capability report schema_version"
            )
        try:
            timestamp = ensure_aware(self.timestamp)
        except (TypeError, ValueError) as error:
            raise InvalidCapabilityError("timestamp is invalid") from error
        if not isinstance(self.justifications, Mapping):
            raise InvalidCapabilityError("justifications must be an object")
        justifications: dict[str, Sequence[str]] = {}
        for key, values in self.justifications.items():
            try:
                normalized_key = require_non_empty(key, "justification key")
                normalized_values = tuple(
                    require_non_empty(item, "justification") for item in values
                )
            except (TypeError, ValueError) as error:
                raise InvalidCapabilityError(str(error)) from error
            if not normalized_values:
                raise InvalidCapabilityError(
                    "justification entries cannot be empty"
                )
            justifications[normalized_key] = normalized_values
        object.__setattr__(self, "missing", missing)
        object.__setattr__(
            self, "justifications", MappingProxyType(justifications)
        )
        object.__setattr__(self, "timestamp", timestamp)

    @property
    def is_valid(self) -> bool:
        """Return whether all mandatory constraints admit a final set."""
        return not self.missing and not self.conflicting

    def to_dict(self) -> dict[str, object]:
        """Return the strict versioned report envelope."""
        return {
            "schema_version": self.schema_version,
            "accepted": self.accepted.to_dict(),
            "rejected": self.rejected.to_dict(),
            "missing": [item.to_dict() for item in self.missing],
            "conflicting": self.conflicting.to_dict(),
            "justifications": {
                key: list(values)
                for key, values in sorted(self.justifications.items())
            },
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
        }

    def to_json(self) -> str:
        """Serialize the report as deterministic JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore a capability report from a strict mapping."""
        expected = {
            "schema_version",
            "accepted",
            "rejected",
            "missing",
            "conflicting",
            "justifications",
            "timestamp",
        }
        _strict(payload, expected, "capability report")
        for name in ("accepted", "rejected", "conflicting"):
            if not isinstance(payload[name], Mapping):
                raise InvalidCapabilityError(f"{name} must be an object")
        missing = payload["missing"]
        justifications = payload["justifications"]
        if not isinstance(missing, list) or any(
            not isinstance(item, Mapping) for item in missing
        ):
            raise InvalidCapabilityError("missing must be an array of objects")
        if not isinstance(justifications, Mapping) or any(
            not isinstance(key, str)
            or not isinstance(values, list)
            or any(not isinstance(item, str) for item in values)
            for key, values in justifications.items()
        ):
            raise InvalidCapabilityError("justifications are invalid")
        timestamp_value = payload["timestamp"]
        if not isinstance(timestamp_value, str):
            raise InvalidCapabilityError("timestamp must be a string")
        try:
            timestamp = datetime.fromisoformat(
                timestamp_value.replace("Z", "+00:00")
            )
        except ValueError as error:
            raise InvalidCapabilityError("timestamp is invalid") from error
        return cls(
            CapabilitySet.from_dict(payload["accepted"]),
            CapabilitySet.from_dict(payload["rejected"]),
            tuple(CapabilityRequirement.from_dict(item) for item in missing),
            CapabilitySet.from_dict(payload["conflicting"]),
            {key: tuple(values) for key, values in justifications.items()},
            timestamp,
            str(payload["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Restore a capability report from deterministic JSON."""
        return cls.from_dict(_object(payload))


__all__ = [
    "CAPABILITY_SCHEMA_VERSION",
    "Capability",
    "CapabilityCategory",
    "CapabilityReport",
    "CapabilityRequirement",
    "CapabilityRequirementType",
    "CapabilitySet",
]
