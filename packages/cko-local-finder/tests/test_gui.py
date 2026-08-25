from __future__ import annotations

import os
from pathlib import Path
import time
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication, QMessageBox

from cko_local_finder.application.facade import IngestRequest, ProgressStage, SearchRequest
from cko_local_finder.bootstrap import create_application
from cko_local_finder.gui.main_window import MainWindow, PROGRESS_TEXT, SOURCE_NOTICE
from cko_local_finder.gui.workers import IngestionWorker


@pytest.fixture(scope="module")
def application():
    instance = QApplication.instance() or QApplication([])
    yield instance


def wait_until(application: QApplication, condition, timeout: float = 8.0) -> None:
    deadline = time.monotonic() + timeout
    while not condition() and time.monotonic() < deadline:
        application.processEvents()
        time.sleep(0.01)
    assert condition()


def test_window_default_database_source_and_normal_close(application, tmp_path: Path) -> None:
    database = tmp_path / "state" / "finder.sqlite3"
    window = MainWindow(create_application(), default_database=database)
    assert database.is_file() and "Banco válido" == window.database_state.text()
    assert SOURCE_NOTICE.startswith("Os arquivos originais não são movidos")
    assert not window.ingest_button.isEnabled()
    window.source = tmp_path
    window._update_controls(True)
    assert window.ingest_button.isEnabled()
    window.close()


def test_alternate_database_validation(application, tmp_path: Path) -> None:
    window = MainWindow(create_application(), default_database=tmp_path / "default.sqlite3")
    alternate = tmp_path / "alternate.sqlite3"
    assert window._validate_database(alternate, create=True)
    assert window.database == alternate and window.database_state.text() == "Banco válido"
    window.close()


def test_all_thirteen_progress_events_have_explicit_text() -> None:
    assert set(PROGRESS_TEXT) == set(ProgressStage)
    assert len(PROGRESS_TEXT) == 13


def test_worker_runs_outside_gui_thread_and_cleans_up(application, tmp_path: Path) -> None:
    root, database = tmp_path / "corpus", tmp_path / "finder.sqlite3"
    root.mkdir()
    (root / "one.txt").write_text("thread token", encoding="utf-8")
    facade = create_application()
    seen: list[QThread] = []
    original = facade.ingest

    def recording(request, *, on_progress=None):
        seen.append(QThread.currentThread())
        return original(request, on_progress=on_progress)

    facade.ingest = recording  # type: ignore[method-assign]
    worker = IngestionWorker(facade, IngestRequest(str(root), str(database)))
    thread = QThread()
    worker.moveToThread(thread)
    success, failure = QSignalSpy(worker.succeeded), QSignalSpy(worker.failed)
    thread.started.connect(worker.run)
    worker.succeeded.connect(thread.quit)
    worker.failed.connect(thread.quit)
    thread.start()
    wait_until(application, lambda: success.count() + failure.count() > 0)
    assert success.count() == 1 and failure.count() == 0
    assert seen and seen[0] is not application.thread()
    wait_until(application, lambda: not thread.isRunning())
    assert thread.wait(1000)
    worker.deleteLater()
    thread.deleteLater()


def test_window_ingestion_search_pagination_details_and_reports(application, tmp_path: Path) -> None:
    root, database = tmp_path / "corpus", tmp_path / "finder.sqlite3"
    root.mkdir()
    for index in range(3):
        (root / f"{index}.txt").write_text(f"desktop token {index}", encoding="utf-8")
    window = MainWindow(create_application(), default_database=database)
    window.source = root
    window.source_label.setText(str(root))
    window.start_ingestion()
    assert not window.ingest_button.isEnabled()
    window.start_ingestion()
    wait_until(application, lambda: window._thread is None)
    assert window.progress.value() == 100
    window.query.setText("desktop")
    window.limit.setValue(1)
    window.search()
    assert window.results.topLevelItemCount() == 1 and window.next_button.isEnabled()
    first = window.results.topLevelItem(0).data(0, 256)
    window.next_page()
    assert window.offset == 1 and window.results.topLevelItem(0).data(0, 256) != first
    window.results.setCurrentItem(window.results.topLevelItem(0))
    window.show_details()
    assert "sha256:" in window.details.toPlainText()
    window.refresh_reports()
    assert "discovered_locations:" in window.report_views["ingestion"].toPlainText()
    assert window.report_views["failure"].toPlainText()
    assert window.report_views["duplicate"].toPlainText()
    window.close()


def test_empty_search_and_filters(application, tmp_path: Path) -> None:
    window = MainWindow(create_application(), default_database=tmp_path / "finder.sqlite3")
    window.query.setText("absent")
    window.extension.setText(".txt")
    window.media_type.setText("text/plain")
    window.search()
    assert window.results.topLevelItemCount() == 0 and window.page_label.text() == "Nenhum resultado"
    window.close()


def test_close_is_refused_while_ingestion_active(application, tmp_path: Path, monkeypatch) -> None:
    window = MainWindow(create_application(), default_database=tmp_path / "finder.sqlite3")
    messages: list[str] = []
    monkeypatch.setattr(QMessageBox, "information", lambda *args: messages.append(args[-1]))
    window._thread = SimpleNamespace()  # type: ignore[assignment]
    event = QCloseEvent()
    window.closeEvent(event)
    assert not event.isAccepted() and "A ingestão está em andamento" in messages[0]
    window._thread = None
    window.close()


def test_partial_failure_is_sanitized_and_prior_success_is_searchable(
        application, tmp_path: Path, monkeypatch) -> None:
    root, database = tmp_path / "corpus", tmp_path / "finder.sqlite3"
    root.mkdir()
    (root / "a.txt").write_text("surviving gui token", encoding="utf-8")
    (root / "b.txt").write_text("fails", encoding="utf-8")
    from cko_local_finder.infrastructure import extractors
    original = extractors.PlainTextExtractor.extract

    def fail_second(self, source):
        if source.relative_path == "b.txt":
            raise RuntimeError("SELECT private document body traceback")
        return original(self, source)

    monkeypatch.setattr(extractors.PlainTextExtractor, "extract", fail_second)
    window = MainWindow(create_application(), default_database=database)
    window.source = root
    window.start_ingestion()
    wait_until(application, lambda: window._thread is None)
    assert window.progress_label.text() == "Falha interna."
    assert "SELECT" not in window.progress_label.text() and "traceback" not in window.progress_label.text()
    page = window.facade.search(SearchRequest("surviving", str(database)))
    assert len(page.results) == 1 and page.results[0].path == "a.txt"
    window.close()
