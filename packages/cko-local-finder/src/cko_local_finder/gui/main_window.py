"""Single-window Qt Widgets adapter for the application facade."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from PySide6.QtCore import QStandardPaths, Qt, QThread, Slot
from PySide6.QtWidgets import (
    QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QProgressBar, QPushButton, QSpinBox, QSplitter,
    QTabWidget, QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

from cko_local_finder.application.facade import (
    ApplicationFacade, IngestRequest, ProgressEvent, ProgressStage, SearchRequest,
)
from cko_local_finder.gui.workers import IngestionWorker


PROGRESS_TEXT = {
    ProgressStage.INGESTION_STARTED: "Ingestão iniciada",
    ProgressStage.DISCOVERY_STARTED: "Localizando documentos",
    ProgressStage.DISCOVERY_COMPLETED: "Localização concluída",
    ProgressStage.PERSISTENCE_STARTED: "Registrando documentos",
    ProgressStage.PERSISTENCE_COMPLETED: "Registro concluído",
    ProgressStage.EXTRACTION_STARTED: "Extraindo conteúdo compatível",
    ProgressStage.EXTRACTION_COMPLETED: "Extração concluída",
    ProgressStage.INDEXING_STARTED: "Indexando documentos",
    ProgressStage.INDEXING_COMPLETED: "Indexação concluída",
    ProgressStage.REPORTING_STARTED: "Preparando relatórios",
    ProgressStage.REPORTING_COMPLETED: "Relatórios atualizados",
    ProgressStage.INGESTION_COMPLETED: "Ingestão concluída",
    ProgressStage.STAGE_FAILED: "Falha na ingestão",
}

SOURCE_NOTICE = (
    "Os arquivos originais não são movidos, alterados ou excluídos automaticamente. "
    "O conteúdo compatível é lido, extraído e indexado localmente no banco selecionado."
)


def default_database_path() -> Path:
    """Return the Qt-selected per-user path without creating it."""
    directory = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
    return Path(directory) / "cko-local-finder.sqlite3"


def _render(value: Any) -> str:
    """Render facade DTOs without exposing document bodies or Python errors."""
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, dict):
        return "\n".join(f"{key}: {_render(item)}" for key, item in value.items())
    if isinstance(value, (tuple, list)):
        return "\n\n".join(_render(item) for item in value) or "Nenhum registro."
    return str(value)


class MainWindow(QMainWindow):
    """The complete minimal desktop workflow in one window."""

    def __init__(self, facade: ApplicationFacade, *, default_database: Path | None = None) -> None:
        super().__init__()
        self.facade = facade
        self.default_database = default_database or default_database_path()
        self.database = self.default_database
        self.source: Path | None = None
        self.offset = 0
        self.page = None
        self._thread: QThread | None = None
        self._worker: IngestionWorker | None = None
        self.setWindowTitle("CKO Local Knowledge Finder")
        self.resize(1100, 760)
        self._build_ui()
        self.use_default_database()

    def _build_ui(self) -> None:
        central, layout = QWidget(), QVBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        database_box, database_row = QGroupBox("Banco local"), QHBoxLayout()
        self.database_label, self.database_state = QLabel(), QLabel()
        select_database = QPushButton("Selecionar banco…")
        select_database.clicked.connect(self.select_database)
        default_database = QPushButton("Usar banco padrão")
        default_database.clicked.connect(self.use_default_database)
        for widget in (self.database_label, select_database, default_database, self.database_state):
            database_row.addWidget(widget)
        database_box.setLayout(database_row)
        layout.addWidget(database_box)

        source_box, source_layout = QGroupBox("Origem e ingestão"), QVBoxLayout()
        source_row = QHBoxLayout()
        self.source_label = QLabel("Nenhuma pasta selecionada")
        select_source = QPushButton("Selecionar pasta…")
        select_source.clicked.connect(self.select_source)
        self.ingest_button = QPushButton("Iniciar ingestão")
        self.ingest_button.clicked.connect(self.start_ingestion)
        source_row.addWidget(self.source_label, 1)
        source_row.addWidget(select_source)
        source_row.addWidget(self.ingest_button)
        notice = QLabel(SOURCE_NOTICE)
        notice.setWordWrap(True)
        self.progress_label, self.progress = QLabel("Aguardando ingestão"), QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        source_layout.addLayout(source_row)
        source_layout.addWidget(notice)
        source_layout.addWidget(self.progress_label)
        source_layout.addWidget(self.progress)
        source_box.setLayout(source_layout)
        layout.addWidget(source_box)

        search_box, search_layout = QGroupBox("Busca"), QFormLayout()
        query_row = QHBoxLayout()
        self.query = QLineEdit()
        self.query.setPlaceholderText("Termos da busca")
        self.search_button = QPushButton("Pesquisar")
        self.search_button.clicked.connect(lambda: self.search(reset=True))
        query_row.addWidget(self.query, 1)
        query_row.addWidget(self.search_button)
        search_layout.addRow("Consulta", query_row)
        filters = QHBoxLayout()
        self.extension, self.media_type = QLineEdit(), QLineEdit()
        self.root_filter, self.path_prefix = QLineEdit(), QLineEdit()
        self.limit = QSpinBox()
        self.limit.setRange(1, 100)
        self.limit.setValue(20)
        for label, widget in (("Extensão", self.extension), ("Tipo", self.media_type),
                              ("Raiz", self.root_filter), ("Prefixo", self.path_prefix),
                              ("Limite", self.limit)):
            filters.addWidget(QLabel(label))
            filters.addWidget(widget)
        search_layout.addRow(filters)
        search_box.setLayout(search_layout)
        layout.addWidget(search_box)

        splitter = QSplitter()
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.results = QTreeWidget()
        self.results.setHeaderLabels(("Título", "Trecho", "Extensão", "Tipo", "Caminho", "Raiz", "Ranking"))
        self.results.itemSelectionChanged.connect(self.show_details)
        pagination = QHBoxLayout()
        self.previous_button, self.next_button = QPushButton("Anterior"), QPushButton("Próxima")
        self.previous_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)
        self.page_label = QLabel("Nenhum resultado")
        pagination.addWidget(self.previous_button)
        pagination.addWidget(self.page_label, 1)
        pagination.addWidget(self.next_button)
        left_layout.addWidget(self.results)
        left_layout.addLayout(pagination)
        splitter.addWidget(left)

        self.tabs = QTabWidget()
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.tabs.addTab(self.details, "Detalhes")
        self.report_views: dict[str, QTextEdit] = {}
        for key, title in (("ingestion", "Relatório de ingestão"), ("failure", "Falhas"),
                           ("duplicate", "Duplicatas")):
            view = QTextEdit()
            view.setReadOnly(True)
            self.report_views[key] = view
            self.tabs.addTab(view, title)
        refresh = QPushButton("Atualizar relatórios")
        refresh.clicked.connect(self.refresh_reports)
        report_panel = QWidget()
        report_layout = QVBoxLayout(report_panel)
        report_layout.addWidget(self.tabs)
        report_layout.addWidget(refresh)
        splitter.addWidget(report_panel)
        layout.addWidget(splitter, 1)
        self._update_controls(False)

    def _update_controls(self, valid: bool) -> None:
        active = self._thread is not None
        self.ingest_button.setEnabled(valid and self.source is not None and not active)
        self.search_button.setEnabled(valid and not active)
        self.previous_button.setEnabled(valid and self.offset > 0 and not active)
        more = bool(self.page and self.offset + self.page.limit < self.page.total_matches)
        self.next_button.setEnabled(valid and more and not active)

    def _validate_database(self, path: Path, *, create: bool) -> bool:
        try:
            if create:
                path.parent.mkdir(parents=True, exist_ok=True)
            capability = self.facade.validate_database(str(path), create=create)
            if capability.schema_version > 3:
                raise ValueError
        except Exception:
            self.database_state.setText("Banco inválido ou incompatível")
            self._update_controls(False)
            return False
        self.database = path
        self.database_label.setText(str(path))
        self.database_state.setText("Banco válido")
        self._update_controls(True)
        return True

    @Slot()
    def use_default_database(self) -> None:
        self._validate_database(self.default_database, create=not self.default_database.is_file())

    @Slot()
    def select_database(self) -> None:
        chosen, _ = QFileDialog.getSaveFileName(self, "Selecionar banco local", str(self.database),
                                                "Banco SQLite (*.sqlite3 *.sqlite);;Todos os arquivos (*)")
        if chosen:
            path = Path(chosen)
            self._validate_database(path, create=not path.is_file())

    @Slot()
    def select_source(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Selecionar pasta de origem")
        if chosen:
            self.source = Path(chosen)
            self.source_label.setText(str(self.source))
            self._update_controls(True)

    @Slot()
    def start_ingestion(self) -> None:
        if self._thread is not None or self.source is None:
            return
        request = IngestRequest(str(self.source), str(self.database))
        thread, worker = QThread(self), IngestionWorker(self.facade, request)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self.on_progress)
        worker.succeeded.connect(self.ingestion_succeeded)
        worker.failed.connect(self.ingestion_failed)
        worker.succeeded.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)
        worker.succeeded.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self.thread_finished)
        self._thread, self._worker = thread, worker
        self.progress.setRange(0, 0)
        self.progress_label.setText("Iniciando ingestão")
        self._update_controls(True)
        thread.start()

    @Slot(object)
    def on_progress(self, event: ProgressEvent) -> None:
        text = PROGRESS_TEXT[event.stage]
        if event.count is not None:
            text += f" ({event.count})"
        self.progress_label.setText(text)

    @Slot(object)
    def ingestion_succeeded(self, result: object) -> None:
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.progress_label.setText("Ingestão concluída")
        self.report_views["ingestion"].setPlainText(_render(getattr(result, "report", result)))

    @Slot(str)
    def ingestion_failed(self, message: str) -> None:
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress_label.setText(message)

    @Slot()
    def thread_finished(self) -> None:
        self._thread = None
        self._worker = None
        self._update_controls(True)
        self.refresh_reports()

    def _text_or_none(self, widget: QLineEdit) -> str | None:
        return widget.text().strip() or None

    @Slot()
    def search(self, *, reset: bool = True) -> None:
        if reset:
            self.offset = 0
        request = SearchRequest(self.query.text(), str(self.database), self.limit.value(),
                                self._text_or_none(self.extension), self._text_or_none(self.media_type),
                                self._text_or_none(self.root_filter), self._text_or_none(self.path_prefix),
                                None, self.offset)
        try:
            self.page = self.facade.search(request)
        except Exception:
            self._show_error("Não foi possível realizar a busca.")
            return
        self.results.clear()
        for result in self.page.results:
            item = QTreeWidgetItem((result.title, result.snippet, result.extension, result.media_type,
                                    result.path, result.root, f"{result.score:.6g}"))
            item.setData(0, Qt.ItemDataRole.UserRole, result.sha256)
            self.results.addTopLevelItem(item)
        self.page_label.setText(
            "Nenhum resultado" if not self.page.total_matches else
            f"{self.offset + 1}–{self.offset + len(self.page.results)} de {self.page.total_matches}"
        )
        self._update_controls(True)

    @Slot()
    def previous_page(self) -> None:
        self.offset = max(0, self.offset - self.limit.value())
        self.search(reset=False)

    @Slot()
    def next_page(self) -> None:
        if self.page and self.offset + self.page.limit < self.page.total_matches:
            self.offset += self.page.limit
            self.search(reset=False)

    @Slot()
    def show_details(self) -> None:
        selected = self.results.selectedItems()
        if not selected:
            return
        try:
            details = self.facade.get_document_details(selected[0].data(0, Qt.ItemDataRole.UserRole),
                                                       str(self.database))
        except Exception:
            self.details.setPlainText("Não foi possível consultar os detalhes.")
        else:
            self.details.setPlainText(_render(details))

    @Slot()
    def refresh_reports(self) -> None:
        try:
            if self.source is not None:
                ingestion = self.facade.get_ingestion_report(str(self.database), str(self.source))
                self.report_views["ingestion"].setPlainText(_render(ingestion))
            failure = self.facade.get_failure_report(str(self.database),
                                                     str(self.source) if self.source else None)
            duplicate = self.facade.get_duplicate_report(str(self.database),
                                                         str(self.source) if self.source else None)
        except Exception:
            self.report_views["failure"].setPlainText("Relatórios indisponíveis.")
            self.report_views["duplicate"].setPlainText("Relatórios indisponíveis.")
        else:
            self.report_views["failure"].setPlainText(_render(failure))
            self.report_views["duplicate"].setPlainText(_render(duplicate))

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "CKO Local Knowledge Finder", message)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API
        if self._thread is not None:
            QMessageBox.information(
                self, "Ingestão em andamento",
                "A ingestão está em andamento.\nAguarde a conclusão antes de fechar a aplicação.",
            )
            event.ignore()
            return
        event.accept()
