"""Background ingestion worker; it never accesses widgets."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from cko_local_finder.application.facade import ApplicationFacade, IngestRequest


class IngestionWorker(QObject):
    """Run one facade ingestion in its owning QThread."""

    progress = Signal(object)
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, facade: ApplicationFacade, request: IngestRequest) -> None:
        super().__init__()
        self._facade = facade
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            result = self._facade.ingest(self._request, on_progress=self.progress.emit)
        except Exception:
            self.failed.emit("Falha interna.")
        else:
            self.succeeded.emit(result)
