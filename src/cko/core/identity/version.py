"""Versionamento semântico para contratos e objetos canônicos."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering


_SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


@total_ordering
@dataclass(frozen=True, slots=True)
class SemanticVersion:
    """Versão compatível com o formato público Semantic Versioning."""

    major: int
    minor: int
    patch: int
    prerelease: str | None = None
    build: str | None = None

    def __post_init__(self) -> None:
        if min(self.major, self.minor, self.patch) < 0:
            raise ValueError("componentes da versão não podem ser negativos")
        self._validate_text()

    def _validate_text(self) -> None:
        if _SEMVER_PATTERN.fullmatch(str(self)) is None:
            raise ValueError("versão semântica inválida")

    @classmethod
    def parse(cls, value: str) -> SemanticVersion:
        """Interpreta uma versão semântica completa."""
        match = _SEMVER_PATTERN.fullmatch(value)
        if match is None:
            raise ValueError(f"versão semântica inválida: {value!r}")
        major, minor, patch, prerelease, build = match.groups()
        return cls(int(major), int(minor), int(patch), prerelease, build)

    def __str__(self) -> str:
        """Serializa a versão no formato canônico."""
        value = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            value += f"-{self.prerelease}"
        if self.build:
            value += f"+{self.build}"
        return value

    def __lt__(self, other: object) -> bool:
        """Compara precedência conforme as regras do Semantic Versioning."""
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        own_core = (self.major, self.minor, self.patch)
        other_core = (other.major, other.minor, other.patch)
        if own_core != other_core:
            return own_core < other_core
        return self._prerelease_key() < other._prerelease_key()

    def _prerelease_key(self) -> tuple[int, tuple[tuple[int, int | str], ...]]:
        if self.prerelease is None:
            return (1, ())
        parts: list[tuple[int, int | str]] = []
        for identifier in self.prerelease.split("."):
            part = (
                (0, int(identifier))
                if identifier.isdigit()
                else (1, identifier)
            )
            parts.append(part)
        return (0, tuple(parts))
