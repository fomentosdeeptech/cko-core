"""Immutable graph metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Mapping

from .contracts import GRAPH_SCHEMA_VERSION, GraphModel, deep_freeze, instant, text
from .enums import GraphStatus
from .errors import GraphValidationError


@dataclass(frozen=True, slots=True)
class GraphMetadata(GraphModel):
    created_at: datetime
    modified_at: datetime
    created_by: str
    status: GraphStatus = GraphStatus.ACTIVE
    category: str | None = None
    attributes: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = GRAPH_SCHEMA_VERSION
    discriminator: ClassVar[str] = "graph_metadata"

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", instant(self.created_at, "created_at"))
        object.__setattr__(self, "modified_at", instant(self.modified_at, "modified_at"))
        if self.modified_at < self.created_at:
            raise GraphValidationError("modified_at cannot precede created_at")
        object.__setattr__(self, "created_by", text(self.created_by, "created_by"))
        try:
            object.__setattr__(self, "status", GraphStatus(self.status))
        except (TypeError, ValueError) as error:
            raise GraphValidationError("status must be GraphStatus") from error
        object.__setattr__(self, "category", text(self.category, "category", optional=True))
        if not isinstance(self.attributes, Mapping):
            raise GraphValidationError("attributes must be a mapping")
        object.__setattr__(self, "attributes", deep_freeze(self.attributes))
        self._validate_schema()


__all__ = ["GraphMetadata"]
