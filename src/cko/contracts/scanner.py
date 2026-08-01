"""Contrato do scanner sem acoplamento à implementação atual."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol


@dataclass(frozen=True, slots=True)
class ScannedFile:
    path: Path
    size_bytes: int


class FileScanner(Protocol):
    def scan(self, root: Path) -> Iterable[ScannedFile]:
        """Descobre arquivos sem mover, renomear ou excluir."""
        ...
