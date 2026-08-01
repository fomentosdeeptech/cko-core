"""Envelope universal de metadados do CKO CORE SDK."""

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Mapping

from cko.core.utils import ensure_aware, require_non_empty


@dataclass(frozen=True, slots=True)
class UniversalMetadata:
    """Metadados técnicos comuns, extensíveis sem regra de produto."""

    media_type: str
    created_at: datetime
    modified_at: datetime
    language: str | None = None
    attributes: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "media_type",
            require_non_empty(self.media_type, "media_type"),
        )
        created_at = ensure_aware(self.created_at)
        modified_at = ensure_aware(self.modified_at)
        if modified_at < created_at:
            raise ValueError("modified_at não pode anteceder created_at")
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "modified_at", modified_at)
        if self.language is not None:
            object.__setattr__(
                self,
                "language",
                require_non_empty(self.language, "language"),
            )
        object.__setattr__(self, "attributes", MappingProxyType(dict(self.attributes)))

