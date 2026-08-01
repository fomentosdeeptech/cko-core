"""Contratos de persistência independentes de SQLite."""

from typing import Protocol
from uuid import UUID

from cko.models.document import DocumentRecord


class DocumentRepository(Protocol):
    def get(self, document_id: UUID) -> DocumentRecord | None:
        """Localiza um documento pela identidade interna."""
        ...

    def add(self, document: DocumentRecord) -> None:
        """Registra um documento."""
        ...
