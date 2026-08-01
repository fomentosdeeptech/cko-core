"""Evento neutro para integração desacoplada entre componentes."""

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Mapping

from cko.core.identity import CanonicalId, Origin
from cko.core.utils import ensure_aware, require_non_empty


@dataclass(frozen=True, slots=True)
class CanonicalEvent:
    """Fato técnico imutável publicável por uma porta de eventos."""

    id: CanonicalId
    name: str
    occurred_at: datetime
    origin: Origin
    attributes: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", require_non_empty(self.name, "name"))
        object.__setattr__(self, "occurred_at", ensure_aware(self.occurred_at))
        object.__setattr__(self, "attributes", MappingProxyType(dict(self.attributes)))

