"""Canonical graph identities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID, uuid4, uuid5

from .contracts import GRAPH_SCHEMA_VERSION, GraphModel, semantic_version, text
from .errors import GraphIdentityError


_GRAPH_UUID_NAMESPACE = UUID("ac032d0c-3e79-4eb0-970e-dd3328e873e4")


@dataclass(frozen=True, order=True, slots=True)
class GraphId(GraphModel):
    value: UUID
    schema_version: str = GRAPH_SCHEMA_VERSION
    discriminator: ClassVar[str] = "graph_id"

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            try:
                object.__setattr__(self, "value", UUID(str(self.value)))
            except (TypeError, ValueError, AttributeError) as error:
                raise GraphIdentityError("value must be a UUID") from error
        self._validate_schema()

    @classmethod
    def new(cls) -> "GraphId":
        return cls(uuid4())

    @classmethod
    def canonical(cls, namespace: str, semantic_key: str) -> "GraphId":
        selected_namespace = text(namespace, "namespace")
        selected_key = text(semantic_key, "semantic_key")
        return cls(uuid5(_GRAPH_UUID_NAMESPACE, f"{selected_namespace}:{selected_key}"))

    @classmethod
    def parse(cls, value: str | UUID) -> "GraphId":
        try:
            return cls(value if isinstance(value, UUID) else UUID(value))
        except (TypeError, ValueError, AttributeError) as error:
            raise GraphIdentityError("value must be a UUID") from error

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class GraphIdentity(GraphModel):
    logical_id: GraphId
    canonical_id: GraphId
    namespace: str
    name: str
    version: str = "1.0.0"
    schema_version: str = GRAPH_SCHEMA_VERSION
    discriminator: ClassVar[str] = "graph_identity"

    def __post_init__(self) -> None:
        if not isinstance(self.logical_id, GraphId) or not isinstance(self.canonical_id, GraphId):
            raise GraphIdentityError("logical_id and canonical_id must be GraphId")
        object.__setattr__(self, "namespace", text(self.namespace, "namespace"))
        object.__setattr__(self, "name", text(self.name, "name"))
        object.__setattr__(self, "version", semantic_version(self.version))
        expected = GraphId.canonical(self.namespace, f"{self.logical_id}:{self.name}")
        if self.canonical_id != expected:
            raise GraphIdentityError("canonical_id does not match graph identity")
        self._validate_schema()


__all__ = ["GraphId", "GraphIdentity"]
