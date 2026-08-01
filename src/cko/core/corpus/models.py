"""Immutable canonical models for logical knowledge corpus composition."""

from __future__ import annotations

import re
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from enum import Enum
from typing import ClassVar, Mapping

from .contracts import (CORPUS_SCHEMA_VERSION, CORPUS_SERIALIZATION_VERSION,
                        CorpusModel, deep_freeze, instant, non_negative,
                        semantic_version, text)
from .enums import CorpusMemberCategory
from .errors import (CorpusCategoryError, CorpusDigestError, CorpusFactoryError,
                     CorpusManifestError, CorpusReferenceError)
from .identity import CorpusId, CorpusIdentity

_FACTORY_TOKEN = object()
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _category(value: object) -> CorpusMemberCategory:
    try:
        return CorpusMemberCategory(value)
    except (TypeError, ValueError) as error:
        raise CorpusCategoryError("category is not admitted by the corpus schema") from error


def _digest(value: object, name: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or _SHA256.fullmatch(value.lower()) is None:
        raise CorpusDigestError(f"{name} must be a SHA-256 hexadecimal digest")
    return value.lower()


@dataclass(frozen=True, slots=True)
class CorpusVersion(CorpusModel):
    version: str
    revision: int = 0
    schema_version: str = CORPUS_SCHEMA_VERSION
    discriminator: ClassVar[str] = "corpus_version"

    def __post_init__(self) -> None:
        object.__setattr__(self, "version", semantic_version(self.version, "corpus_version"))
        object.__setattr__(self, "revision", non_negative(self.revision, "revision"))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class CorpusMemberReference(CorpusModel):
    member_id: str
    category: CorpusMemberCategory
    member_version: str
    discriminator_name: str
    namespace: str
    member_digest: str | None = None
    attributes: Mapping[str, object] = field(default_factory=dict, hash=False)
    schema_version: str = CORPUS_SCHEMA_VERSION
    discriminator: ClassVar[str] = "corpus_member_reference"

    def __post_init__(self) -> None:
        object.__setattr__(self, "member_id", text(self.member_id, "member_id"))
        object.__setattr__(self, "category", _category(self.category))
        object.__setattr__(self, "member_version", semantic_version(self.member_version, "member_version"))
        object.__setattr__(self, "discriminator_name", text(self.discriminator_name, "discriminator_name"))
        object.__setattr__(self, "namespace", text(self.namespace, "namespace"))
        object.__setattr__(self, "member_digest", _digest(self.member_digest, "member_digest", optional=True))
        object.__setattr__(self, "attributes", deep_freeze(self.attributes))
        self._validate_schema()

    @property
    def identity_key(self) -> tuple[str, str, str]:
        return (self.category.value, self.namespace, self.member_id)

    @property
    def sort_token(self) -> tuple[str, ...]:
        return (*self.identity_key, self.member_version, self.member_digest or "", self.discriminator_name)


@dataclass(frozen=True, slots=True)
class CorpusManifest(CorpusModel):
    members: tuple[CorpusMemberReference, ...] = ()
    schema_version: str = CORPUS_SCHEMA_VERSION
    discriminator: ClassVar[str] = "corpus_manifest"

    def __post_init__(self) -> None:
        members = tuple(self.members)
        if any(not isinstance(member, CorpusMemberReference) for member in members):
            raise CorpusManifestError("members must contain CorpusMemberReference values")
        keys = [member.identity_key for member in members]
        if len(keys) != len(set(keys)):
            raise CorpusManifestError("manifest member identities must be unique")
        object.__setattr__(self, "members", tuple(sorted(members, key=lambda item: item.sort_token)))
        self._validate_schema()

    def __len__(self) -> int:
        return len(self.members)

    def __iter__(self):
        return iter(self.members)


@dataclass(frozen=True, slots=True)
class CorpusMetadata(CorpusModel):
    description: str | None = None
    labels: tuple[str, ...] = ()
    attributes: Mapping[str, object] = field(default_factory=dict, hash=False)
    schema_version: str = CORPUS_SCHEMA_VERSION
    discriminator: ClassVar[str] = "corpus_metadata"

    def __post_init__(self) -> None:
        object.__setattr__(self, "description", text(self.description, "description", optional=True))
        labels = tuple(text(label, "label") for label in self.labels)
        if len(labels) != len(set(labels)):
            raise CorpusManifestError("metadata labels must be unique")
        object.__setattr__(self, "labels", tuple(sorted(labels)))
        object.__setattr__(self, "attributes", deep_freeze(self.attributes))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class KnowledgeCorpus(CorpusModel):
    identity: CorpusIdentity
    corpus_version: CorpusVersion
    manifest: CorpusManifest
    metadata: CorpusMetadata
    digest: str
    serialization_version: str = CORPUS_SERIALIZATION_VERSION
    schema_version: str = CORPUS_SCHEMA_VERSION
    _factory_token: InitVar[object | None] = None
    discriminator: ClassVar[str] = "knowledge_corpus"

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _FACTORY_TOKEN:
            raise CorpusFactoryError("KnowledgeCorpus must be created by CorpusFactory")
        if not isinstance(self.identity, CorpusIdentity):
            raise CorpusReferenceError("identity must be CorpusIdentity")
        if not isinstance(self.corpus_version, CorpusVersion):
            raise CorpusReferenceError("corpus_version must be CorpusVersion")
        if not isinstance(self.manifest, CorpusManifest):
            raise CorpusReferenceError("manifest must be CorpusManifest")
        if not isinstance(self.metadata, CorpusMetadata):
            raise CorpusReferenceError("metadata must be CorpusMetadata")
        object.__setattr__(self, "digest", _digest(self.digest, "digest"))
        if self.serialization_version != CORPUS_SERIALIZATION_VERSION:
            raise CorpusReferenceError("unsupported serialization_version")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class CorpusStatistics(CorpusModel):
    total_members: int
    members_with_digest: int
    categories_present: int
    by_category: Mapping[str, int] = field(hash=False)
    by_member_version: Mapping[str, int] = field(hash=False)
    schema_version: str = CORPUS_SCHEMA_VERSION
    discriminator: ClassVar[str] = "corpus_statistics"

    def __post_init__(self) -> None:
        for name in ("total_members", "members_with_digest", "categories_present"):
            object.__setattr__(self, name, non_negative(getattr(self, name), name))
        if self.members_with_digest > self.total_members:
            raise CorpusManifestError("members_with_digest cannot exceed total_members")
        if self.categories_present > len(CorpusMemberCategory):
            raise CorpusManifestError("categories_present exceeds the closed category set")
        for name in ("by_category", "by_member_version"):
            value = getattr(self, name)
            if not isinstance(value, Mapping) or any(not isinstance(count, int) or count < 0 for count in value.values()):
                raise CorpusManifestError(f"{name} must map strings to non-negative integers")
            object.__setattr__(self, name, deep_freeze(value))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class CorpusReferenceChange(CorpusModel):
    before: CorpusMemberReference
    after: CorpusMemberReference
    version_changed: bool
    digest_changed: bool
    schema_version: str = CORPUS_SCHEMA_VERSION
    discriminator: ClassVar[str] = "corpus_reference_change"

    def __post_init__(self) -> None:
        if not isinstance(self.before, CorpusMemberReference) or not isinstance(self.after, CorpusMemberReference):
            raise CorpusReferenceError("reference changes require canonical references")
        if self.before.identity_key != self.after.identity_key:
            raise CorpusReferenceError("changed references must have the same member identity")
        if not isinstance(self.version_changed, bool) or not isinstance(self.digest_changed, bool):
            raise CorpusReferenceError("change flags must be boolean")
        if not self.version_changed and not self.digest_changed and self.before == self.after:
            raise CorpusReferenceError("reference change must describe a structural change")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class CorpusComparisonResult(CorpusModel):
    added: tuple[CorpusMemberReference, ...] = ()
    removed: tuple[CorpusMemberReference, ...] = ()
    preserved: tuple[CorpusMemberReference, ...] = ()
    changed: tuple[CorpusReferenceChange, ...] = ()
    schema_version: str = CORPUS_SCHEMA_VERSION
    discriminator: ClassVar[str] = "corpus_comparison_result"

    def __post_init__(self) -> None:
        for name in ("added", "removed", "preserved"):
            values = tuple(getattr(self, name))
            if any(not isinstance(value, CorpusMemberReference) for value in values):
                raise CorpusManifestError(f"{name} must contain corpus references")
            object.__setattr__(self, name, tuple(sorted(values, key=lambda item: item.sort_token)))
        changes = tuple(self.changed)
        if any(not isinstance(value, CorpusReferenceChange) for value in changes):
            raise CorpusManifestError("changed must contain CorpusReferenceChange values")
        object.__setattr__(self, "changed", tuple(sorted(changes, key=lambda item: item.before.sort_token)))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class CorpusSnapshot(CorpusModel):
    snapshot_id: CorpusId
    corpus_id: CorpusId
    corpus_version: CorpusVersion
    manifest: CorpusManifest
    digest: str
    statistics: CorpusStatistics
    captured_at: datetime
    schema_version: str = CORPUS_SCHEMA_VERSION
    discriminator: ClassVar[str] = "corpus_snapshot"

    def __post_init__(self) -> None:
        if not isinstance(self.snapshot_id, CorpusId) or not isinstance(self.corpus_id, CorpusId):
            raise CorpusReferenceError("snapshot identifiers must be CorpusId")
        if not isinstance(self.corpus_version, CorpusVersion) or not isinstance(self.manifest, CorpusManifest):
            raise CorpusReferenceError("snapshot has invalid structural models")
        if not isinstance(self.statistics, CorpusStatistics):
            raise CorpusReferenceError("statistics must be CorpusStatistics")
        object.__setattr__(self, "digest", _digest(self.digest, "digest"))
        object.__setattr__(self, "captured_at", instant(self.captured_at, "captured_at"))
        self._validate_schema()


__all__ = [
    "CorpusComparisonResult", "CorpusManifest", "CorpusMemberReference",
    "CorpusMetadata", "CorpusReferenceChange", "CorpusSnapshot",
    "CorpusStatistics", "CorpusVersion", "KnowledgeCorpus",
]
