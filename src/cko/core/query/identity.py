"""Canonical query identities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID, uuid4, uuid5

from .contracts import QUERY_SCHEMA_VERSION, QueryModel, semantic_version, text
from .errors import QueryIdentityError


_QUERY_UUID_NAMESPACE = UUID("e432fd3e-7fc8-4f7b-8e12-b7a84de86014")


@dataclass(frozen=True, order=True, slots=True)
class QueryId(QueryModel):
    value: UUID
    schema_version: str = QUERY_SCHEMA_VERSION
    discriminator: ClassVar[str] = "query_id"

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            try:
                object.__setattr__(self, "value", UUID(str(self.value)))
            except (TypeError, ValueError, AttributeError) as error:
                raise QueryIdentityError("value must be a UUID") from error
        self._validate_schema()

    @classmethod
    def new(cls) -> "QueryId":
        return cls(uuid4())

    @classmethod
    def canonical(cls, namespace: str, semantic_key: str) -> "QueryId":
        selected_namespace = text(namespace, "namespace")
        selected_key = text(semantic_key, "semantic_key")
        return cls(uuid5(_QUERY_UUID_NAMESPACE, f"{selected_namespace}:{selected_key}"))

    @classmethod
    def parse(cls, value: str | UUID) -> "QueryId":
        try:
            return cls(value if isinstance(value, UUID) else UUID(value))
        except (TypeError, ValueError, AttributeError) as error:
            raise QueryIdentityError("value must be a UUID") from error

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class QueryIdentity(QueryModel):
    logical_id: QueryId
    canonical_id: QueryId
    namespace: str
    name: str
    version: str = "1.0.0"
    schema_version: str = QUERY_SCHEMA_VERSION
    discriminator: ClassVar[str] = "query_identity"

    def __post_init__(self) -> None:
        if not isinstance(self.logical_id, QueryId) or not isinstance(self.canonical_id, QueryId):
            raise QueryIdentityError("logical_id and canonical_id must be QueryId")
        object.__setattr__(self, "namespace", text(self.namespace, "namespace"))
        object.__setattr__(self, "name", text(self.name, "name"))
        object.__setattr__(self, "version", semantic_version(self.version))
        expected = QueryId.canonical(self.namespace, f"{self.logical_id}:{self.name}")
        if self.canonical_id != expected:
            raise QueryIdentityError("canonical_id does not match query identity")
        self._validate_schema()


__all__ = ["QueryId", "QueryIdentity"]
