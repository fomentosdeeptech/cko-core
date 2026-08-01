"""Proveniência mínima de objetos produzidos ou observados pelo SDK."""

from dataclasses import dataclass
from datetime import datetime

from cko.core.utils import ensure_aware, require_non_empty


@dataclass(frozen=True, slots=True)
class Origin:
    """Origem técnica rastreável, sem incorporar decisão de governança."""

    system: str
    captured_at: datetime
    reference: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "system", require_non_empty(self.system, "system"))
        object.__setattr__(self, "captured_at", ensure_aware(self.captured_at))
        if self.reference is not None:
            object.__setattr__(
                self,
                "reference",
                require_non_empty(self.reference, "reference"),
            )

