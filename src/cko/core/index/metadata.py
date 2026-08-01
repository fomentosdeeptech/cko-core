"""Immutable structural metadata for canonical indexes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Mapping

from .contracts import INDEX_SCHEMA_VERSION, IndexModel, deep_freeze, instant, text
from .enums import IndexStatus
from .errors import IndexValidationError


@dataclass(frozen=True, slots=True)
class IndexMetadata(IndexModel):
    created_at: datetime
    updated_at: datetime
    created_by: str
    status: IndexStatus = IndexStatus.ACTIVE
    attributes: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = INDEX_SCHEMA_VERSION
    discriminator: ClassVar[str] = "index_metadata"
    def __post_init__(self) -> None:
        object.__setattr__(self,"created_at",instant(self.created_at,"created_at"))
        object.__setattr__(self,"updated_at",instant(self.updated_at,"updated_at"))
        if self.updated_at < self.created_at: raise IndexValidationError("updated_at cannot precede created_at")
        object.__setattr__(self,"created_by",text(self.created_by,"created_by"))
        try: object.__setattr__(self,"status",IndexStatus(self.status))
        except (TypeError,ValueError) as error: raise IndexValidationError("status must be IndexStatus") from error
        object.__setattr__(self,"attributes",deep_freeze(self.attributes))
        self._validate_schema()


__all__=["IndexMetadata"]
