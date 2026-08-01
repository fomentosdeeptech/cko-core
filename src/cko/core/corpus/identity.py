"""Stable and deterministic identities for logical knowledge corpora."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID, uuid4, uuid5

from .contracts import CORPUS_SCHEMA_VERSION, CorpusModel, text
from .errors import CorpusIdentityError

CORPUS_UUID_NAMESPACE = UUID("0d0ee5a8-e17e-5ae1-b9e4-7801131bf190")


@dataclass(frozen=True, order=True, slots=True)
class CorpusId(CorpusModel):
    value: UUID
    schema_version: str = CORPUS_SCHEMA_VERSION
    discriminator: ClassVar[str] = "corpus_id"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "value", self.value if isinstance(self.value, UUID) else UUID(str(self.value)))
        except (TypeError, ValueError, AttributeError) as error:
            raise CorpusIdentityError("value must be a UUID") from error
        self._validate_schema()

    @classmethod
    def new(cls) -> "CorpusId":
        return cls(uuid4())

    @classmethod
    def canonical(cls, namespace: str, structural_key: str) -> "CorpusId":
        key = f"{text(namespace, 'namespace')}:{text(structural_key, 'structural_key')}"
        return cls(uuid5(CORPUS_UUID_NAMESPACE, key))

    @classmethod
    def parse(cls, value: str | UUID) -> "CorpusId":
        return cls(value)  # type: ignore[arg-type]

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class CorpusIdentity(CorpusModel):
    corpus_id: CorpusId
    namespace: str
    name: str
    schema_version: str = CORPUS_SCHEMA_VERSION
    discriminator: ClassVar[str] = "corpus_identity"

    def __post_init__(self) -> None:
        if not isinstance(self.corpus_id, CorpusId):
            raise CorpusIdentityError("corpus_id must be CorpusId")
        object.__setattr__(self, "namespace", text(self.namespace, "namespace"))
        object.__setattr__(self, "name", text(self.name, "name"))
        expected = CorpusId.canonical(self.namespace, self.name)
        if self.corpus_id != expected:
            raise CorpusIdentityError("corpus_id does not match namespace and name")
        self._validate_schema()


__all__ = ["CORPUS_UUID_NAMESPACE", "CorpusId", "CorpusIdentity"]
