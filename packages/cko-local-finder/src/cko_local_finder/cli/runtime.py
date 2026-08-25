"""Thin CLI adapter over the shared application composition root."""

from typing import Any

from cko_local_finder.application.facade import ApplicationFacade, IngestRequest, IngestResult, SearchRequest
from cko_local_finder.bootstrap import (
    ExtractorRegistry, RequiredResourceUnavailable, _repository, discover_files,
)


def _application() -> ApplicationFacade:
    """Compose through bootstrap-owned adapters while retaining test seams."""
    return ApplicationFacade(_repository, discover_files, ExtractorRegistry)


def ingest(root: str, database: str, *, include_hidden: bool = False,
           follow_symlinks: bool = False) -> IngestResult:
    return _application().ingest(IngestRequest(root, database, include_hidden, follow_symlinks))


def search(query: str, database: str, *, limit: int = 20, extension: str | None = None,
           media_type: str | None = None, root: str | None = None,
           path_prefix: str | None = None, sha256: str | None = None):
    return _application().search(SearchRequest(
        query, database, limit, extension, media_type, root, path_prefix, sha256,
    ))


def show(sha256: str, database: str):
    return _application().get_document_details(sha256, database)


def duplicates(database: str, *, root: str | None = None):
    return _application().get_duplicate_report(database, root)


def report(report_type: str, database: str, *, root: str | None = None) -> Any:
    application = _application()
    if report_type == "ingestion":
        if root is None:
            raise ValueError("ingestion report requires --root")
        return application.get_ingestion_report(database, root)
    if report_type == "failures":
        return application.get_failure_report(database, root)
    return application.get_duplicate_report(database, root)
