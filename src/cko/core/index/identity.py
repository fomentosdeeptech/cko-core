"""Deterministic logical and canonical index identities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID, uuid4, uuid5

from .contracts import INDEX_SCHEMA_VERSION, IndexModel, semantic_version, text
from .errors import IndexIdentityError

_INDEX_UUID_NAMESPACE = UUID("a991df55-391c-53c6-b83a-b6de53e1f9a6")


@dataclass(frozen=True, order=True, slots=True)
class IndexId(IndexModel):
    value: UUID
    schema_version: str = INDEX_SCHEMA_VERSION
    discriminator: ClassVar[str] = "index_id"
    def __post_init__(self) -> None:
        try: object.__setattr__(self, "value", self.value if isinstance(self.value, UUID) else UUID(str(self.value)))
        except (TypeError, ValueError, AttributeError) as error: raise IndexIdentityError("value must be a UUID") from error
        self._validate_schema()
    @classmethod
    def new(cls) -> "IndexId": return cls(uuid4())
    @classmethod
    def canonical(cls, namespace: str, structural_key: str) -> "IndexId":
        return cls(uuid5(_INDEX_UUID_NAMESPACE, f"{text(namespace,'namespace')}:{text(structural_key,'structural_key')}"))
    @classmethod
    def parse(cls, value: str | UUID) -> "IndexId": return cls(value)  # type: ignore[arg-type]
    def __str__(self) -> str: return str(self.value)


@dataclass(frozen=True, slots=True)
class IndexIdentity(IndexModel):
    logical_id: IndexId
    canonical_id: IndexId
    definition_id: IndexId
    namespace: str
    name: str
    version: str = "1.0.0"
    schema_version: str = INDEX_SCHEMA_VERSION
    discriminator: ClassVar[str] = "index_identity"
    def __post_init__(self) -> None:
        if any(not isinstance(v, IndexId) for v in (self.logical_id,self.canonical_id,self.definition_id)):
            raise IndexIdentityError("index identity identifiers must be IndexId")
        object.__setattr__(self,"namespace",text(self.namespace,"namespace"))
        object.__setattr__(self,"name",text(self.name,"name"))
        object.__setattr__(self,"version",semantic_version(self.version))
        expected=IndexId.canonical(self.namespace,f"{self.logical_id}:{self.definition_id}:{self.version}")
        if self.canonical_id != expected: raise IndexIdentityError("canonical_id does not match structural identity")
        self._validate_schema()


__all__=["IndexId","IndexIdentity"]
