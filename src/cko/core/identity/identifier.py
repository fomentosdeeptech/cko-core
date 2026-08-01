"""Tipo de identidade baseado em UUID para entidades canônicas."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, order=True, slots=True)
class CanonicalId:
    """UUID fortemente tipado usado nas fronteiras públicas do SDK."""

    value: UUID

    @classmethod
    def new(cls) -> CanonicalId:
        """Cria uma identidade aleatória UUID versão 4."""
        return cls(uuid4())

    @classmethod
    def parse(cls, value: str | UUID) -> CanonicalId:
        """Converte texto ou ``UUID`` em identidade canônica."""
        return cls(value if isinstance(value, UUID) else UUID(value))

    def __str__(self) -> str:
        """Retorna a representação UUID normalizada."""
        return str(self.value)

