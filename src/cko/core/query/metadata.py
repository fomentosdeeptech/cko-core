"""Immutable metadata for canonical query intent."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Mapping

from .contracts import QUERY_SCHEMA_VERSION, QueryModel, deep_freeze, instant, text, unique_texts
from .enums import QueryStatus
from .errors import QueryValidationError


@dataclass(frozen=True, slots=True)
class QueryMetadata(QueryModel):
    created_at: datetime
    modified_at: datetime
    created_by: str
    status: QueryStatus = QueryStatus.READY
    tags: tuple[str, ...] = ()
    attributes: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = QUERY_SCHEMA_VERSION
    discriminator: ClassVar[str] = "query_metadata"

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", instant(self.created_at, "created_at"))
        object.__setattr__(self, "modified_at", instant(self.modified_at, "modified_at"))
        if self.modified_at < self.created_at:
            raise QueryValidationError("modified_at cannot precede created_at")
        object.__setattr__(self, "created_by", text(self.created_by, "created_by"))
        try:
            object.__setattr__(self, "status", QueryStatus(self.status))
        except (TypeError, ValueError) as error:
            raise QueryValidationError("status must be QueryStatus") from error
        object.__setattr__(self, "tags", unique_texts(self.tags, "tags"))
        if not isinstance(self.attributes, Mapping):
            raise QueryValidationError("attributes must be a mapping")
        object.__setattr__(self, "attributes", deep_freeze(self.attributes))
        self._validate_schema()


__all__ = ["QueryMetadata"]
