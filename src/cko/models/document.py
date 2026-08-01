"""Identidades documentais independentes do caminho físico."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    document_id: UUID
    sha256: str
    size_bytes: int
    discovered_at: datetime

    def __post_init__(self) -> None:
        if len(self.sha256) != 64:
            raise ValueError("sha256 deve conter 64 caracteres")
        if self.size_bytes < 0:
            raise ValueError("size_bytes não pode ser negativo")


@dataclass(frozen=True, slots=True)
class FileLocationRecord:
    location_id: UUID
    document_id: UUID
    path: Path
    observed_at: datetime
