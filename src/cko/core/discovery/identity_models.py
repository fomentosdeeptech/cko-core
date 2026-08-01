"""Immutable, versioned models for Discovery identity resolution."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Self

from cko.core.identity import CanonicalId
from cko.core.utils import ensure_aware, require_non_empty

from .identity_errors import (
    InvalidIdentityCandidateError,
    InvalidIdentityEvidenceError,
    InvalidIdentityPolicyError,
    InvalidIdentityResolutionRequestError,
)
from .models import DiscoveredItem, DiscoveryContext
from .session import DiscoverySession


IDENTITY_RESOLUTION_SCHEMA_VERSION = "1.0"


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, float, str, CanonicalId)):
        return value
    if isinstance(value, datetime):
        return ensure_aware(value)
    if isinstance(value, Enum):
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, nested in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("mapping keys must be non-empty strings")
            frozen[key] = _freeze(nested)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    raise TypeError(f"unsupported identity value: {type(value).__name__}")


def _primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, CanonicalId):
        return str(value)
    if isinstance(value, datetime):
        return ensure_aware(value).isoformat().replace("+00:00", "Z")
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_primitive(item) for item in value]
    if hasattr(value, "to_dict"):
        return value.to_dict()  # type: ignore[no-any-return, union-attr]
    raise TypeError(f"unsupported identity value: {type(value).__name__}")


def _json(payload: Mapping[str, object]) -> str:
    return json.dumps(
        _primitive(payload), ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )


def _datetime(value: object, error_type: type[ValueError]) -> datetime:
    if not isinstance(value, str):
        raise error_type("timestamp must be an ISO 8601 string")
    try:
        return ensure_aware(datetime.fromisoformat(value.replace("Z", "+00:00")))
    except ValueError as error:
        raise error_type("timestamp is invalid") from error


def _object(payload: str, error_type: type[ValueError]) -> Mapping[str, object]:
    try:
        decoded = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as error:
        raise error_type("identity JSON is invalid") from error
    if not isinstance(decoded, dict):
        raise error_type("identity JSON must contain an object")
    return decoded


def _strict(
    payload: Mapping[str, object],
    expected: set[str],
    model: str,
    error_type: type[ValueError],
) -> None:
    unknown = set(payload) - expected
    missing = expected - set(payload)
    if unknown:
        raise error_type(f"unknown {model} fields: {sorted(unknown)}")
    if missing:
        raise error_type(f"missing {model} fields: {sorted(missing)}")
    if payload.get("schema_version") != IDENTITY_RESOLUTION_SCHEMA_VERSION:
        raise error_type(f"unsupported {model} schema_version")


def _confidence(value: float, name: str, error_type: type[ValueError]) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0.0 <= value <= 1.0
    ):
        raise error_type(f"{name} must be between 0.0 and 1.0")
    return float(value)


class IdentityEvidenceType(str, Enum):
    """Canonical kinds of already-available identity evidence."""

    EXTERNAL_IDENTIFIER = "external_identifier"
    DECLARED_CHECKSUM = "declared_checksum"
    NORMALIZED_LOGICAL_NAME = "normalized_logical_name"
    MEDIA_TYPE = "media_type"
    DECLARED_SIZE = "declared_size"
    DECLARED_TIMESTAMP = "declared_timestamp"
    SOURCE_KEY = "source_key"
    CANONICAL_ATTRIBUTE = "canonical_attribute"
    COMPOSITE = "composite"


class ResolutionStatus(str, Enum):
    """Canonical outcomes of identity resolution."""

    RESOLVED_EXISTING = "resolved_existing"
    RESOLVED_NEW = "resolved_new"
    DUPLICATE_CANDIDATE = "duplicate_candidate"
    AMBIGUOUS = "ambiguous"
    CONFLICT = "conflict"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    REJECTED = "rejected"


class ConflictSeverity(str, Enum):
    """Severity assigned to a conflicting comparable value."""

    WARNING = "warning"
    ERROR = "error"


class ConflictBehavior(str, Enum):
    """Policy behavior when conflicts are detected."""

    REPORT = "report"
    REJECT = "reject"


class InsufficientEvidenceBehavior(str, Enum):
    """Policy behavior when mandatory evidence is absent."""

    REPORT = "report"
    REJECT = "reject"


@dataclass(frozen=True, slots=True)
class IdentityEvidence:
    """Public immutable evidence supplied without I/O or content access."""

    evidence_type: IdentityEvidenceType
    key: str
    value: object
    source: str
    confidence: float = 1.0
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = IDENTITY_RESOLUTION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        try:
            kind = IdentityEvidenceType(self.evidence_type)
            key = require_non_empty(self.key, "key")
            source = require_non_empty(self.source, "source")
            if self.value is None:
                raise ValueError("value cannot be null")
            value = _freeze(self.value)
            metadata = _freeze(self.metadata)
            confidence = _confidence(
                self.confidence, "confidence", InvalidIdentityEvidenceError
            )
        except (TypeError, ValueError) as error:
            if isinstance(error, InvalidIdentityEvidenceError):
                raise
            raise InvalidIdentityEvidenceError(str(error)) from error
        if self.schema_version != IDENTITY_RESOLUTION_SCHEMA_VERSION:
            raise InvalidIdentityEvidenceError("unsupported evidence schema_version")
        object.__setattr__(self, "evidence_type", kind)
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "metadata", metadata)
        object.__setattr__(self, "confidence", confidence)

    def to_dict(self) -> dict[str, object]:
        """Return the strict versioned evidence envelope."""
        return {
            "schema_version": self.schema_version,
            "evidence_type": self.evidence_type.value,
            "key": self.key,
            "value": _primitive(self.value),
            "source": self.source,
            "confidence": self.confidence,
            "metadata": _primitive(self.metadata),
        }

    def to_json(self) -> str:
        """Serialize evidence as deterministic JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore evidence while rejecting unknown fields and versions."""
        expected = {
            "schema_version", "evidence_type", "key", "value", "source",
            "confidence", "metadata",
        }
        _strict(payload, expected, "evidence", InvalidIdentityEvidenceError)
        metadata = payload["metadata"]
        if not isinstance(metadata, Mapping):
            raise InvalidIdentityEvidenceError("metadata must be an object")
        return cls(
            IdentityEvidenceType(str(payload["evidence_type"])),
            str(payload["key"]), payload["value"], str(payload["source"]),
            payload["confidence"], metadata, str(payload["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Restore evidence from deterministic JSON."""
        return cls.from_dict(_object(payload, InvalidIdentityEvidenceError))


@dataclass(frozen=True, slots=True)
class IdentityFingerprint:
    """Deterministic logical fingerprint derived only from supplied values."""

    value: str
    components: tuple[str, ...]
    scheme: str = "cko.logical.identity.sha256"
    schema_version: str = IDENTITY_RESOLUTION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != IDENTITY_RESOLUTION_SCHEMA_VERSION:
            raise InvalidIdentityEvidenceError("unsupported fingerprint schema_version")
        if len(self.value) != 64 or any(char not in "0123456789abcdef" for char in self.value):
            raise InvalidIdentityEvidenceError("fingerprint value must be lowercase SHA-256")
        components = tuple(require_non_empty(item, "component") for item in self.components)
        if not components or len(set(components)) != len(components):
            raise InvalidIdentityEvidenceError("fingerprint components must be unique")
        object.__setattr__(self, "components", components)
        object.__setattr__(self, "scheme", require_non_empty(self.scheme, "scheme"))

    @classmethod
    def create(cls, evidence: tuple[IdentityEvidence, ...]) -> Self:
        """Create a logical fingerprint without reading or hashing a file."""
        if not evidence:
            raise InvalidIdentityEvidenceError("fingerprint requires evidence")
        ordered = sorted(
            evidence,
            key=lambda item: (item.evidence_type.value, item.key, item.to_json()),
        )
        components = tuple(
            f"{item.evidence_type.value}:{item.key}" for item in ordered
        )
        if len(set(components)) != len(components):
            raise InvalidIdentityEvidenceError("fingerprint evidence keys must be unique")
        material = _json({"schema_version": IDENTITY_RESOLUTION_SCHEMA_VERSION,
                          "evidence": [item.to_dict() for item in ordered]})
        return cls(hashlib.sha256(material.encode("utf-8")).hexdigest(), components)

    def to_dict(self) -> dict[str, object]:
        """Return the versioned fingerprint envelope."""
        return {"schema_version": self.schema_version, "scheme": self.scheme,
                "value": self.value, "components": list(self.components)}

    def to_json(self) -> str:
        """Serialize the fingerprint as deterministic JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore a logical fingerprint from a strict mapping."""
        expected = {"schema_version", "scheme", "value", "components"}
        _strict(payload, expected, "fingerprint", InvalidIdentityEvidenceError)
        components = payload["components"]
        if not isinstance(components, list):
            raise InvalidIdentityEvidenceError("components must be an array")
        return cls(str(payload["value"]), tuple(str(item) for item in components),
                   str(payload["scheme"]), str(payload["schema_version"]))

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Restore a logical fingerprint from JSON."""
        return cls.from_dict(_object(payload, InvalidIdentityEvidenceError))


@dataclass(frozen=True, slots=True)
class IdentityCandidate:
    """Possible externally supplied canonical asset match."""

    canonical_id: CanonicalId
    attributes: Mapping[str, object]
    evidence: tuple[IdentityEvidence, ...]
    logical_origin: str
    confidence: float
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = IDENTITY_RESOLUTION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        try:
            if not isinstance(self.canonical_id, CanonicalId):
                raise TypeError("canonical_id must be CanonicalId")
            attributes = _freeze(self.attributes)
            evidence = tuple(self.evidence)
            if any(not isinstance(item, IdentityEvidence) for item in evidence):
                raise TypeError("evidence must contain IdentityEvidence")
            origin = require_non_empty(self.logical_origin, "logical_origin")
            confidence = _confidence(
                self.confidence, "confidence", InvalidIdentityCandidateError
            )
            metadata = _freeze(self.metadata)
        except (TypeError, ValueError) as error:
            if isinstance(error, InvalidIdentityCandidateError):
                raise
            raise InvalidIdentityCandidateError(str(error)) from error
        if self.schema_version != IDENTITY_RESOLUTION_SCHEMA_VERSION:
            raise InvalidIdentityCandidateError("unsupported candidate schema_version")
        object.__setattr__(self, "attributes", attributes)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "logical_origin", origin)
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "metadata", metadata)

    def to_dict(self) -> dict[str, object]:
        """Return the strict versioned candidate envelope."""
        return {"schema_version": self.schema_version,
                "canonical_id": str(self.canonical_id),
                "attributes": _primitive(self.attributes),
                "evidence": [item.to_dict() for item in self.evidence],
                "logical_origin": self.logical_origin,
                "confidence": self.confidence,
                "metadata": _primitive(self.metadata)}

    def to_json(self) -> str:
        """Serialize the candidate as deterministic JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore a candidate from a strict mapping."""
        expected = {"schema_version", "canonical_id", "attributes", "evidence",
                    "logical_origin", "confidence", "metadata"}
        _strict(payload, expected, "candidate", InvalidIdentityCandidateError)
        attributes = payload["attributes"]
        metadata = payload["metadata"]
        evidence = payload["evidence"]
        if (
            not isinstance(attributes, Mapping)
            or not isinstance(metadata, Mapping)
            or not isinstance(evidence, list)
        ):
            raise InvalidIdentityCandidateError("candidate collections are invalid")
        try:
            canonical_id = CanonicalId.parse(str(payload["canonical_id"]))
            restored = tuple(
                IdentityEvidence.from_dict(item)
                for item in evidence
                if isinstance(item, Mapping)
            )
        except (TypeError, ValueError) as error:
            raise InvalidIdentityCandidateError("candidate payload is invalid") from error
        if len(restored) != len(evidence):
            raise InvalidIdentityCandidateError("candidate evidence is invalid")
        return cls(canonical_id, attributes, restored, str(payload["logical_origin"]),
                   payload["confidence"], metadata, str(payload["schema_version"]))

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Restore a candidate from JSON."""
        return cls.from_dict(_object(payload, InvalidIdentityCandidateError))


@dataclass(frozen=True, slots=True)
class IdentityConflict:
    """Auditable difference between observation and candidate values."""

    attribute: str
    observed_value: object
    candidate_value: object
    severity: ConflictSeverity
    evidence: IdentityEvidence
    code: str
    description: str
    schema_version: str = IDENTITY_RESOLUTION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "attribute", require_non_empty(self.attribute, "attribute"))
        object.__setattr__(self, "observed_value", _freeze(self.observed_value))
        object.__setattr__(self, "candidate_value", _freeze(self.candidate_value))
        object.__setattr__(self, "severity", ConflictSeverity(self.severity))
        if not isinstance(self.evidence, IdentityEvidence):
            raise InvalidIdentityEvidenceError("conflict evidence is invalid")
        object.__setattr__(self, "code", require_non_empty(self.code, "code"))
        object.__setattr__(self, "description", require_non_empty(self.description, "description"))
        if self.schema_version != IDENTITY_RESOLUTION_SCHEMA_VERSION:
            raise InvalidIdentityEvidenceError("unsupported conflict schema_version")

    def to_dict(self) -> dict[str, object]:
        """Return an auditable conflict representation."""
        return {"schema_version": self.schema_version,
                "attribute": self.attribute,
                "observed_value": _primitive(self.observed_value),
                "candidate_value": _primitive(self.candidate_value),
                "severity": self.severity.value,
                "evidence": self.evidence.to_dict(), "code": self.code,
                "description": self.description}

    def to_json(self) -> str:
        """Serialize the conflict as deterministic JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore a conflict from a strict versioned mapping."""
        expected = {
            "schema_version", "attribute", "observed_value", "candidate_value",
            "severity", "evidence", "code", "description",
        }
        _strict(payload, expected, "conflict", InvalidIdentityEvidenceError)
        evidence = payload["evidence"]
        if not isinstance(evidence, Mapping):
            raise InvalidIdentityEvidenceError("conflict evidence is invalid")
        return cls(
            attribute=str(payload["attribute"]),
            observed_value=payload["observed_value"],
            candidate_value=payload["candidate_value"],
            severity=ConflictSeverity(str(payload["severity"])),
            evidence=IdentityEvidence.from_dict(evidence),
            code=str(payload["code"]),
            description=str(payload["description"]),
            schema_version=str(payload["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Restore a conflict from JSON."""
        return cls.from_dict(_object(payload, InvalidIdentityEvidenceError))


@dataclass(frozen=True, slots=True)
class EvidenceEvaluation:
    """Deterministic explanation of an observation/candidate comparison."""

    candidate: IdentityCandidate
    favorable: tuple[IdentityEvidence, ...]
    contrary: tuple[IdentityEvidence, ...]
    missing: tuple[str, ...]
    score: float
    confidence: float
    conflicts: tuple[IdentityConflict, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.candidate, IdentityCandidate):
            raise InvalidIdentityCandidateError("evaluation candidate is invalid")
        for name in ("favorable", "contrary"):
            values = tuple(getattr(self, name))
            if any(not isinstance(item, IdentityEvidence) for item in values):
                raise InvalidIdentityEvidenceError(f"{name} evidence is invalid")
            object.__setattr__(self, name, values)
        object.__setattr__(self, "missing", tuple(sorted(set(self.missing))))
        object.__setattr__(
            self, "score",
            _confidence(self.score, "score", InvalidIdentityEvidenceError),
        )
        object.__setattr__(
            self, "confidence",
            _confidence(self.confidence, "confidence", InvalidIdentityEvidenceError),
        )
        conflicts = tuple(self.conflicts)
        if any(not isinstance(item, IdentityConflict) for item in conflicts):
            raise InvalidIdentityEvidenceError("conflicts are invalid")
        object.__setattr__(self, "conflicts", conflicts)

    def to_dict(self) -> dict[str, object]:
        """Return the complete deterministic evaluation explanation."""
        return {"candidate": self.candidate.to_dict(),
                "favorable": [item.to_dict() for item in self.favorable],
                "contrary": [item.to_dict() for item in self.contrary],
                "missing": list(self.missing), "score": self.score,
                "confidence": self.confidence,
                "conflicts": [item.to_dict() for item in self.conflicts]}


@dataclass(frozen=True, slots=True)
class ResolutionPolicy:
    """Validated immutable thresholds and declarative evidence weights."""

    minimum_match_confidence: float = 0.85
    minimum_duplicate_confidence: float = 0.60
    minimum_candidate_margin: float = 0.10
    required_attributes: tuple[str, ...] = ()
    conflict_behavior: ConflictBehavior = ConflictBehavior.REPORT
    insufficient_evidence_behavior: InsufficientEvidenceBehavior = (
        InsufficientEvidenceBehavior.REPORT
    )
    allow_new_identity: bool = True
    max_candidates: int = 100
    evidence_weights: Mapping[str, float] = field(default_factory=dict)
    schema_version: str = IDENTITY_RESOLUTION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        try:
            match = _confidence(
                self.minimum_match_confidence,
                "minimum_match_confidence",
                InvalidIdentityPolicyError,
            )
            duplicate = _confidence(
                self.minimum_duplicate_confidence,
                "minimum_duplicate_confidence",
                InvalidIdentityPolicyError,
            )
            margin = _confidence(
                self.minimum_candidate_margin,
                "minimum_candidate_margin",
                InvalidIdentityPolicyError,
            )
            if duplicate > match:
                raise InvalidIdentityPolicyError(
                    "duplicate threshold cannot exceed match threshold"
                )
            required = tuple(
                require_non_empty(item, "required_attribute")
                for item in self.required_attributes
            )
            if len(set(required)) != len(required):
                raise InvalidIdentityPolicyError("required_attributes cannot contain duplicates")
            if isinstance(self.max_candidates, bool) or self.max_candidates <= 0:
                raise InvalidIdentityPolicyError("max_candidates must be greater than zero")
            weights: dict[str, float] = {}
            for key, value in self.evidence_weights.items():
                weights[require_non_empty(key, "evidence weight key")] = _confidence(
                    value, "evidence weight", InvalidIdentityPolicyError
                )
            if any(value == 0.0 for value in weights.values()):
                raise InvalidIdentityPolicyError("evidence weights must be greater than zero")
        except (TypeError, ValueError) as error:
            if isinstance(error, InvalidIdentityPolicyError):
                raise
            raise InvalidIdentityPolicyError(str(error)) from error
        if self.schema_version != IDENTITY_RESOLUTION_SCHEMA_VERSION:
            raise InvalidIdentityPolicyError("unsupported policy schema_version")
        object.__setattr__(self, "minimum_match_confidence", match)
        object.__setattr__(self, "minimum_duplicate_confidence", duplicate)
        object.__setattr__(self, "minimum_candidate_margin", margin)
        object.__setattr__(self, "required_attributes", required)
        object.__setattr__(self, "conflict_behavior", ConflictBehavior(self.conflict_behavior))
        object.__setattr__(
            self,
            "insufficient_evidence_behavior",
            InsufficientEvidenceBehavior(self.insufficient_evidence_behavior),
        )
        object.__setattr__(self, "evidence_weights", MappingProxyType(weights))

    def to_dict(self) -> dict[str, object]:
        """Return the strict versioned policy envelope."""
        return {"schema_version": self.schema_version,
                "minimum_match_confidence": self.minimum_match_confidence,
                "minimum_duplicate_confidence": self.minimum_duplicate_confidence,
                "minimum_candidate_margin": self.minimum_candidate_margin,
                "required_attributes": list(self.required_attributes),
                "conflict_behavior": self.conflict_behavior.value,
                "insufficient_evidence_behavior": self.insufficient_evidence_behavior.value,
                "allow_new_identity": self.allow_new_identity,
                "max_candidates": self.max_candidates,
                "evidence_weights": dict(self.evidence_weights)}

    def to_json(self) -> str:
        """Serialize the policy as deterministic JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore a policy from a strict mapping."""
        expected = {"schema_version", "minimum_match_confidence", "minimum_duplicate_confidence",
                    "minimum_candidate_margin", "required_attributes", "conflict_behavior",
                    "insufficient_evidence_behavior", "allow_new_identity", "max_candidates",
                    "evidence_weights"}
        _strict(payload, expected, "policy", InvalidIdentityPolicyError)
        required, weights = payload["required_attributes"], payload["evidence_weights"]
        if not isinstance(required, list) or not isinstance(weights, Mapping):
            raise InvalidIdentityPolicyError("policy collections are invalid")
        return cls(payload["minimum_match_confidence"], payload["minimum_duplicate_confidence"],
                   payload["minimum_candidate_margin"], tuple(str(item) for item in required),
                   ConflictBehavior(str(payload["conflict_behavior"])),
                   InsufficientEvidenceBehavior(str(payload["insufficient_evidence_behavior"])),
                   bool(payload["allow_new_identity"]), payload["max_candidates"], weights,
                   str(payload["schema_version"]))

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Restore a policy from JSON."""
        return cls.from_dict(_object(payload, InvalidIdentityPolicyError))


@dataclass(frozen=True, slots=True)
class IdentityResolutionRequest:
    """Canonical request containing only supplied resolution inputs."""

    item: DiscoveredItem
    session: DiscoverySession
    context: DiscoveryContext
    evidence: tuple[IdentityEvidence, ...]
    policy: ResolutionPolicy
    known_candidates: tuple[IdentityCandidate, ...] = ()
    schema_version: str = IDENTITY_RESOLUTION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        try:
            if not isinstance(self.item, DiscoveredItem):
                raise TypeError("item must be DiscoveredItem")
            if not isinstance(self.session, DiscoverySession):
                raise TypeError("session must be DiscoverySession")
            if not isinstance(self.context, DiscoveryContext):
                raise TypeError("context must be DiscoveryContext")
            if self.context != self.session.context:
                raise ValueError("context must match DiscoverySession context")
            if self.item.correlation_id != self.context.correlation_id:
                raise ValueError("item and context correlation identifiers must match")
            evidence = tuple(self.evidence)
            candidates = tuple(self.known_candidates)
            if any(not isinstance(item, IdentityEvidence) for item in evidence):
                raise TypeError("evidence must contain IdentityEvidence")
            if any(not isinstance(item, IdentityCandidate) for item in candidates):
                raise TypeError("known_candidates must contain IdentityCandidate")
            if not isinstance(self.policy, ResolutionPolicy):
                raise TypeError("policy must be ResolutionPolicy")
            identifiers = [item.canonical_id for item in candidates]
            if len(set(identifiers)) != len(identifiers):
                raise ValueError("known_candidates cannot contain duplicate CanonicalId values")
        except (TypeError, ValueError) as error:
            raise InvalidIdentityResolutionRequestError(str(error)) from error
        if self.schema_version != IDENTITY_RESOLUTION_SCHEMA_VERSION:
            raise InvalidIdentityResolutionRequestError("unsupported request schema_version")
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "known_candidates", candidates)

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic audit envelope without serializing session state."""
        return {"schema_version": self.schema_version, "item": self.item.to_dict(),
                "session_id": str(self.session.id), "context": self.context.to_dict(),
                "evidence": [item.to_dict() for item in self.evidence],
                "policy": self.policy.to_dict(),
                "known_candidates": [item.to_dict() for item in self.known_candidates]}

    def to_json(self) -> str:
        """Serialize request inputs as deterministic JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
        session: DiscoverySession,
    ) -> Self:
        """Restore inputs while retaining the explicitly injected session."""
        expected = {
            "schema_version", "item", "session_id", "context", "evidence",
            "policy", "known_candidates",
        }
        _strict(
            payload,
            expected,
            "resolution request",
            InvalidIdentityResolutionRequestError,
        )
        if not isinstance(session, DiscoverySession):
            raise InvalidIdentityResolutionRequestError(
                "session must be DiscoverySession"
            )
        if str(session.id) != payload["session_id"]:
            raise InvalidIdentityResolutionRequestError("session_id does not match")
        item_payload = payload["item"]
        context_payload = payload["context"]
        evidence_payload = payload["evidence"]
        policy_payload = payload["policy"]
        candidates_payload = payload["known_candidates"]
        if (
            not isinstance(item_payload, Mapping)
            or not isinstance(context_payload, Mapping)
            or not isinstance(evidence_payload, list)
            or not isinstance(policy_payload, Mapping)
            or not isinstance(candidates_payload, list)
        ):
            raise InvalidIdentityResolutionRequestError(
                "resolution request collections are invalid"
            )
        try:
            restored_evidence = tuple(
                IdentityEvidence.from_dict(item)
                for item in evidence_payload
                if isinstance(item, Mapping)
            )
            restored_candidates = tuple(
                IdentityCandidate.from_dict(item)
                for item in candidates_payload
                if isinstance(item, Mapping)
            )
            if len(restored_evidence) != len(evidence_payload):
                raise ValueError("request evidence is invalid")
            if len(restored_candidates) != len(candidates_payload):
                raise ValueError("request candidates are invalid")
            return cls(
                item=DiscoveredItem.from_dict(item_payload),
                session=session,
                context=DiscoveryContext.from_dict(context_payload),
                evidence=restored_evidence,
                policy=ResolutionPolicy.from_dict(policy_payload),
                known_candidates=restored_candidates,
                schema_version=str(payload["schema_version"]),
            )
        except (TypeError, ValueError) as error:
            if isinstance(error, InvalidIdentityResolutionRequestError):
                raise
            raise InvalidIdentityResolutionRequestError(
                "resolution request payload is invalid"
            ) from error

    @classmethod
    def from_json(cls, payload: str, session: DiscoverySession) -> Self:
        """Restore request inputs from JSON and an injected session."""
        return cls.from_dict(
            _object(payload, InvalidIdentityResolutionRequestError),
            session,
        )


@dataclass(frozen=True, slots=True)
class ResolutionDecision:
    """Immutable, auditable resolution outcome."""

    status: ResolutionStatus
    canonical_id: CanonicalId | None
    selected_candidate: IdentityCandidate | None
    considered_candidates: tuple[IdentityCandidate, ...]
    confidence: float
    evidence_used: tuple[IdentityEvidence, ...]
    conflicts: tuple[IdentityConflict, ...]
    warnings: tuple[str, ...]
    justification: Mapping[str, object]
    timestamp: datetime
    request_id: str
    session_id: CanonicalId
    schema_version: str = IDENTITY_RESOLUTION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        status = ResolutionStatus(self.status)
        if self.schema_version != IDENTITY_RESOLUTION_SCHEMA_VERSION:
            raise InvalidIdentityResolutionRequestError("unsupported decision schema_version")
        if self.canonical_id is not None and not isinstance(self.canonical_id, CanonicalId):
            raise InvalidIdentityResolutionRequestError("canonical_id must be CanonicalId")
        if (
            status in {
                ResolutionStatus.RESOLVED_EXISTING,
                ResolutionStatus.RESOLVED_NEW,
            }
            and self.canonical_id is None
        ):
            raise InvalidIdentityResolutionRequestError("resolved decisions require CanonicalId")
        if status is ResolutionStatus.RESOLVED_EXISTING and self.selected_candidate is None:
            raise InvalidIdentityResolutionRequestError(
                "resolved_existing requires selected_candidate"
            )
        if status is ResolutionStatus.RESOLVED_NEW and self.selected_candidate is not None:
            raise InvalidIdentityResolutionRequestError("resolved_new cannot select a candidate")
        if status is ResolutionStatus.AMBIGUOUS and self.selected_candidate is not None:
            raise InvalidIdentityResolutionRequestError("ambiguous cannot select a candidate")
        conflicts = tuple(self.conflicts)
        if status is ResolutionStatus.CONFLICT and not conflicts:
            raise InvalidIdentityResolutionRequestError("conflict decision requires conflicts")
        if status is ResolutionStatus.INSUFFICIENT_EVIDENCE and self.canonical_id is not None:
            raise InvalidIdentityResolutionRequestError(
                "insufficient evidence cannot fabricate identity"
            )
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "considered_candidates", tuple(self.considered_candidates))
        object.__setattr__(
            self,
            "confidence",
            _confidence(
                self.confidence,
                "confidence",
                InvalidIdentityResolutionRequestError,
            ),
        )
        object.__setattr__(self, "evidence_used", tuple(self.evidence_used))
        object.__setattr__(self, "conflicts", conflicts)
        object.__setattr__(
            self,
            "warnings",
            tuple(require_non_empty(item, "warning") for item in self.warnings),
        )
        object.__setattr__(self, "justification", _freeze(self.justification))
        object.__setattr__(self, "timestamp", ensure_aware(self.timestamp))
        object.__setattr__(self, "request_id", require_non_empty(self.request_id, "request_id"))
        if not isinstance(self.session_id, CanonicalId):
            raise InvalidIdentityResolutionRequestError("session_id must be CanonicalId")

    def to_dict(self) -> dict[str, object]:
        """Return the complete versioned audit decision."""
        return {"schema_version": self.schema_version, "status": self.status.value,
                "canonical_id": None if self.canonical_id is None else str(self.canonical_id),
                "selected_candidate": (
                    None
                    if self.selected_candidate is None
                    else self.selected_candidate.to_dict()
                ),
                "considered_candidates": [item.to_dict() for item in self.considered_candidates],
                "confidence": self.confidence,
                "evidence_used": [item.to_dict() for item in self.evidence_used],
                "conflicts": [item.to_dict() for item in self.conflicts],
                "warnings": list(self.warnings), "justification": _primitive(self.justification),
                "timestamp": _primitive(self.timestamp), "request_id": self.request_id,
                "session_id": str(self.session_id)}

    def to_json(self) -> str:
        """Serialize the decision as deterministic JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore a complete decision while rejecting unknown fields."""
        expected = {
            "schema_version", "status", "canonical_id", "selected_candidate",
            "considered_candidates", "confidence", "evidence_used", "conflicts",
            "warnings", "justification", "timestamp", "request_id", "session_id",
        }
        _strict(payload, expected, "decision", InvalidIdentityResolutionRequestError)
        selected_payload = payload["selected_candidate"]
        considered_payload = payload["considered_candidates"]
        evidence_payload = payload["evidence_used"]
        conflicts_payload = payload["conflicts"]
        warnings = payload["warnings"]
        justification = payload["justification"]
        if (
            selected_payload is not None and not isinstance(selected_payload, Mapping)
        ):
            raise InvalidIdentityResolutionRequestError(
                "selected_candidate is invalid"
            )
        if (
            not isinstance(considered_payload, list)
            or not isinstance(evidence_payload, list)
            or not isinstance(conflicts_payload, list)
            or not isinstance(warnings, list)
            or not isinstance(justification, Mapping)
        ):
            raise InvalidIdentityResolutionRequestError(
                "decision collections are invalid"
            )
        try:
            selected = (
                None
                if selected_payload is None
                else IdentityCandidate.from_dict(selected_payload)
            )
            considered = tuple(
                IdentityCandidate.from_dict(item)
                for item in considered_payload
                if isinstance(item, Mapping)
            )
            evidence = tuple(
                IdentityEvidence.from_dict(item)
                for item in evidence_payload
                if isinstance(item, Mapping)
            )
            conflicts = tuple(
                IdentityConflict.from_dict(item)
                for item in conflicts_payload
                if isinstance(item, Mapping)
            )
            if (
                len(considered) != len(considered_payload)
                or len(evidence) != len(evidence_payload)
                or len(conflicts) != len(conflicts_payload)
            ):
                raise ValueError("decision collection member is invalid")
            canonical_value = payload["canonical_id"]
            canonical_id = (
                None
                if canonical_value is None
                else CanonicalId.parse(str(canonical_value))
            )
            return cls(
                status=ResolutionStatus(str(payload["status"])),
                canonical_id=canonical_id,
                selected_candidate=selected,
                considered_candidates=considered,
                confidence=payload["confidence"],
                evidence_used=evidence,
                conflicts=conflicts,
                warnings=tuple(str(item) for item in warnings),
                justification=justification,
                timestamp=_datetime(
                    payload["timestamp"], InvalidIdentityResolutionRequestError
                ),
                request_id=str(payload["request_id"]),
                session_id=CanonicalId.parse(str(payload["session_id"])),
                schema_version=str(payload["schema_version"]),
            )
        except (TypeError, ValueError) as error:
            if isinstance(error, InvalidIdentityResolutionRequestError):
                raise
            raise InvalidIdentityResolutionRequestError(
                "decision payload is invalid"
            ) from error

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Restore a complete decision from JSON."""
        return cls.from_dict(
            _object(payload, InvalidIdentityResolutionRequestError)
        )


__all__ = [
    "ConflictBehavior", "ConflictSeverity", "EvidenceEvaluation",
    "IDENTITY_RESOLUTION_SCHEMA_VERSION", "IdentityCandidate", "IdentityConflict",
    "IdentityEvidence", "IdentityEvidenceType", "IdentityFingerprint",
    "IdentityResolutionRequest", "InsufficientEvidenceBehavior", "ResolutionDecision",
    "ResolutionPolicy", "ResolutionStatus",
]
