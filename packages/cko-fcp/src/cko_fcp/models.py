"""Immutable logical types, identities, records, and four state axes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
from typing import Self

from ._validation import instant, optional_text, strict_mapping, string_tuple, text
from .errors import IdentityError, InvalidRecordError, ValidationError


class Maturity(str, Enum):
    LOCATED = "located"
    REGISTERED = "registered"
    VERIFIED = "verified"
    CURATED = "curated"
    OFFICIAL = "official"


class Publication(str, Enum):
    UNPUBLISHED = "unpublished"
    PUBLISHED = "published"
    SUSPENDED = "suspended"
    WITHDRAWN = "withdrawn"
    REJECTED = "rejected"


class Visibility(str, Enum):
    PUBLIC = "public"
    INSTITUTIONAL = "institutional"
    RESTRICTED = "restricted"
    EXISTENCE_RESTRICTED = "existence_restricted"


class Trust(str, Enum):
    T0 = "T0"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"


@dataclass(frozen=True, slots=True, order=True)
class FCPVersion:
    major: int
    minor: int

    def __post_init__(self) -> None:
        if type(self.major) is not int or type(self.minor) is not int:
            raise ValidationError("version components must be integers")
        if self.major < 0 or self.minor < 0:
            raise ValidationError("version components must be non-negative")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"

    @classmethod
    def parse(cls, value: object) -> Self:
        if type(value) is not str or re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", value) is None:
            raise ValidationError("FCP version must use canonical major.minor form")
        major, minor = value.split(".")
        return cls(int(major), int(minor))


@dataclass(frozen=True, slots=True)
class SourceIdentity:
    source_id: str
    local_id: str
    source_revision: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", text(self.source_id, "source_id", IdentityError))
        object.__setattr__(self, "local_id", text(self.local_id, "local_id", IdentityError))
        object.__setattr__(
            self,
            "source_revision",
            optional_text(self.source_revision, "source_revision", IdentityError),
        )

    @classmethod
    def from_dict(cls, value: object) -> Self:
        data = strict_mapping(
            value, {"source_id", "local_id", "source_revision"}, set(), "source_identity", IdentityError
        )
        return cls(data["source_id"], data["local_id"], data["source_revision"])  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class RecordState:
    maturity: Maturity
    publication: Publication
    visibility: Visibility
    trust: Trust

    def __post_init__(self) -> None:
        for field, kind in (
            ("maturity", Maturity), ("publication", Publication),
            ("visibility", Visibility), ("trust", Trust),
        ):
            if not isinstance(getattr(self, field), kind):
                raise InvalidRecordError(f"state.{field} must be {kind.__name__}")

    @classmethod
    def from_dict(cls, value: object) -> Self:
        data = strict_mapping(
            value, {"maturity", "publication", "visibility", "trust"}, set(), "state", InvalidRecordError
        )
        try:
            return cls(
                Maturity(data["maturity"]), Publication(data["publication"]),
                Visibility(data["visibility"]), Trust(data["trust"]),
            )
        except (TypeError, ValueError) as exc:
            raise InvalidRecordError("state contains an unknown value") from exc


@dataclass(frozen=True, slots=True)
class Lifecycle:
    observed_at: datetime
    valid_until: datetime | None
    retention_policy_ref: str
    withdrawal_policy_ref: str

    def __post_init__(self) -> None:
        observed = instant(self.observed_at, "observed_at", InvalidRecordError)
        valid = None if self.valid_until is None else instant(self.valid_until, "valid_until", InvalidRecordError)
        if valid is not None and valid <= observed:
            raise InvalidRecordError("valid_until must be later than observed_at")
        object.__setattr__(self, "observed_at", observed)
        object.__setattr__(self, "valid_until", valid)
        object.__setattr__(self, "retention_policy_ref", text(self.retention_policy_ref, "retention_policy_ref", InvalidRecordError))
        object.__setattr__(self, "withdrawal_policy_ref", text(self.withdrawal_policy_ref, "withdrawal_policy_ref", InvalidRecordError))


@dataclass(frozen=True, slots=True)
class CatalogRecord:
    record_id: str
    record_version: str
    fcp_version: FCPVersion
    asset_class: str
    asset_type: str
    purpose: str
    description: str
    source_identity: SourceIdentity
    authority_refs: tuple[str, ...]
    owner_ref: str
    steward_ref: str | None
    custody_refs: tuple[str, ...]
    state: RecordState
    access_policy_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    relationship_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    lifecycle: Lifecycle

    def __post_init__(self) -> None:
        for field in ("record_id", "record_version", "asset_class", "asset_type", "purpose", "description", "owner_ref"):
            object.__setattr__(self, field, text(getattr(self, field), field, InvalidRecordError))
        if not isinstance(self.fcp_version, FCPVersion):
            raise InvalidRecordError("fcp_version must be FCPVersion")
        if not isinstance(self.source_identity, SourceIdentity):
            raise InvalidRecordError("source_identity must be SourceIdentity")
        if not isinstance(self.state, RecordState):
            raise InvalidRecordError("state must be RecordState")
        if not isinstance(self.lifecycle, Lifecycle):
            raise InvalidRecordError("lifecycle must be Lifecycle")
        object.__setattr__(self, "steward_ref", optional_text(self.steward_ref, "steward_ref", InvalidRecordError))
        for field, required in (
            ("authority_refs", True), ("custody_refs", False), ("access_policy_refs", True),
            ("provenance_refs", True), ("relationship_refs", False), ("limitation_refs", False),
        ):
            object.__setattr__(self, field, string_tuple(getattr(self, field), field, allow_empty=not required, error_type=InvalidRecordError))
        self._validate_invariants()

    def _validate_invariants(self) -> None:
        maturity_rank = list(Maturity).index(self.state.maturity)
        trust_rank = list(Trust).index(self.state.trust)
        if maturity_rank >= list(Maturity).index(Maturity.VERIFIED) and trust_rank < 2:
            raise InvalidRecordError("verified-or-higher maturity requires T2 or higher")
        if self.state.maturity is Maturity.CURATED and (self.steward_ref is None or trust_rank < 3):
            raise InvalidRecordError("curated maturity requires a steward and T3 or higher")
        if self.state.maturity is Maturity.OFFICIAL and trust_rank != 4:
            raise InvalidRecordError("official maturity requires T4")
        if self.state.publication is Publication.PUBLISHED:
            if maturity_rank < 2 or trust_rank < 2:
                raise InvalidRecordError("published records require verified/T2 or higher")
            if self.asset_class in {"dataset", "corpus"} and self.steward_ref is None:
                raise InvalidRecordError("published dataset/corpus requires a steward")
        if self.state.maturity is Maturity.LOCATED and self.state.publication is not Publication.UNPUBLISHED:
            raise InvalidRecordError("located observations must remain unpublished")
