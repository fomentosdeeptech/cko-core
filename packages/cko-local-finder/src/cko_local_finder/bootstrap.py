"""Shared concrete composition root for CLI and future desktop adapters."""

from pathlib import Path

from cko_local_finder.application.facade import ApplicationFacade
from cko_local_finder.infrastructure.extractors import ExtractorRegistry
from cko_local_finder.infrastructure.filesystem import discover_files
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository


class RequiredResourceUnavailable(RuntimeError):
    """A required local runtime capability is unavailable."""


def _repository(database: str, create: bool) -> SQLiteDocumentRepository:
    path = Path(database).expanduser()
    if not create and not path.is_file():
        raise FileNotFoundError("database not found")
    repository = SQLiteDocumentRepository(path)
    if not repository.capabilities().fts5_available:
        raise RequiredResourceUnavailable("FTS5 is unavailable")
    return repository


def create_application() -> ApplicationFacade:
    """Return a fresh, fully composed facade with no mutable global state."""
    return ApplicationFacade(_repository, discover_files, ExtractorRegistry)
