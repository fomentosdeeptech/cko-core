"""Single-window, user-centred Qt Widgets adapter for the application facade."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from PySide6.QtCore import QStandardPaths, Qt, QThread, Slot
from PySide6.QtWidgets import (
    QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QProgressBar, QPushButton, QSpinBox, QSplitter, QTabWidget,
    QTextEdit, QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)
from cko_local_finder.application.facade import (
    ApplicationFacade, IngestRequest, ProgressEvent, ProgressStage, SearchRequest,
)
from cko_local_finder.gui.workers import IngestionWorker

PROGRESS_TEXT = {
    ProgressStage.INGESTION_STARTED: "Preparando a indexação",
    ProgressStage.DISCOVERY_STARTED: "Localizando documentos",
    ProgressStage.DISCOVERY_COMPLETED: "Documentos localizados",
    ProgressStage.PERSISTENCE_STARTED: "Preparando a biblioteca local",
    ProgressStage.PERSISTENCE_COMPLETED: "Biblioteca local preparada",
    ProgressStage.EXTRACTION_STARTED: "Lendo o conteúdo compatível",
    ProgressStage.EXTRACTION_COMPLETED: "Leitura de conteúdo concluída",
    ProgressStage.INDEXING_STARTED: "Indexando documentos para pesquisa",
    ProgressStage.INDEXING_COMPLETED: "Documentos indexados",
    ProgressStage.REPORTING_STARTED: "Preparando o resumo",
    ProgressStage.REPORTING_COMPLETED: "Resumo preparado",
    ProgressStage.INGESTION_COMPLETED: "Indexação concluída",
    ProgressStage.STAGE_FAILED: "Não foi possível concluir a indexação",
}
SOURCE_NOTICE = ("Os arquivos originais não são movidos, alterados ou excluídos automaticamente. "
                 "O CKO apenas lê, extrai e indexa localmente o conteúdo compatível.")
EMPTY_NO_SOURCE = "Adicione uma pasta para começar."
EMPTY_NO_DOCUMENTS = "Indexe uma pasta para preparar sua biblioteca."
EMPTY_NO_SEARCH = "Digite palavras para pesquisar seus documentos."
EMPTY_NO_RESULTS = "Nenhum documento corresponde à busca."
EMPTY_NO_SELECTION = "Selecione um documento para ver os detalhes."
EMPTY_NO_FAILURES = "Nenhum problema encontrado."
EMPTY_NO_DUPLICATES = "Nenhuma duplicata encontrada."
FRIENDLY_TYPES = {
    "application/pdf": "PDF",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Documento Word",
    "text/plain": "Texto", "text/markdown": "Markdown",
}


def default_database_path() -> Path:
    directory = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
    return Path(directory) / "cko-local-finder.sqlite3"


def friendly_type(media_type: str, extension: str = "") -> str:
    if media_type in FRIENDLY_TYPES:
        return FRIENDLY_TYPES[media_type]
    return extension.lstrip(".").upper() or "Documento"


def _render(value: Any) -> str:
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, dict):
        return "\n".join(f"{key}: {_render(item)}" for key, item in value.items())
    if isinstance(value, (tuple, list)):
        return "\n\n".join(_render(item) for item in value) or "Nenhum registro."
    return str(value)


def _format_size(size: int) -> str:
    value = float(size)
    for unit in ("bytes", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{int(value)} {unit}" if unit == "bytes" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} bytes"


def _abbreviated_path(path: Path) -> str:
    parts = path.parts
    return str(path) if len(parts) <= 3 else str(Path(parts[0], "…", *parts[-2:]))


def _ingestion_text(report: Any) -> str:
    return "\n".join((f"Arquivos encontrados: {report.discovered_locations}",
        f"Documentos únicos: {report.unique_documents}",
        f"Documentos indexados: {report.indexed_documents}",
        f"Falhas: {report.recoverable_failures}", f"Grupos de duplicatas: {report.duplicate_groups}"))


def _failure_text(report: Any) -> str:
    issues = tuple(report.issues) + tuple(report.unresolved_historical_issues)
    if not issues:
        return EMPTY_NO_FAILURES
    return "\n\n".join(f"Documento: {i.relative_path or 'Não identificado'}\nEtapa: {i.stage}\n"
        f"Mensagem: {i.message}\nSituação: {'recuperável' if i.recoverable else 'requer atenção'}" for i in issues)


def _duplicate_text(report: Any) -> str:
    if not report.duplicates:
        return EMPTY_NO_DUPLICATES
    return "\n\n".join(f"Este documento aparece em {len(d.origins)} locais:\n" +
        "\n".join(f"  • {o.relative_path} — {o.root}" for o in d.origins) for d in report.duplicates)


class MainWindow(QMainWindow):
    def __init__(self, facade: ApplicationFacade, *, default_database: Path | None = None) -> None:
        super().__init__()
        self.facade, self.default_database = facade, default_database or default_database_path()
        self.database, self.source, self.offset, self.page = self.default_database, None, 0, None
        self._thread: QThread | None = None
        self._worker: IngestionWorker | None = None
        self.setWindowTitle("CKO Local Knowledge Finder")
        self.resize(1100, 760)
        self.setMinimumSize(820, 600)
        self._build_ui()
        self.use_default_database()

    def _build_ui(self) -> None:
        central, layout = QWidget(), QVBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        box, row = QGroupBox("Biblioteca local"), QHBoxLayout()
        self.database_label, self.database_state = QLabel(), QLabel()
        self.database_label.setAccessibleName("Local da biblioteca")
        self.select_database_button = QPushButton("Alterar biblioteca…")
        self.default_database_button = QPushButton("Usar biblioteca padrão")
        self.select_database_button.clicked.connect(self.select_database)
        self.default_database_button.clicked.connect(self.use_default_database)
        for widget in (self.database_label, self.select_database_button,
                       self.default_database_button, self.database_state):
            row.addWidget(widget, 1 if widget is self.database_label else 0)
        box.setLayout(row); layout.addWidget(box)

        box, column, row = QGroupBox("Pasta de documentos"), QVBoxLayout(), QHBoxLayout()
        source_text = QVBoxLayout()
        self.source_label, self.source_path_label = QLabel("Nenhuma pasta selecionada"), QLabel(EMPTY_NO_SOURCE)
        source_text.addWidget(self.source_label); source_text.addWidget(self.source_path_label)
        self.select_source_button, self.ingest_button = QPushButton("Adicionar pasta…"), QPushButton("Indexar pasta")
        self.select_source_button.clicked.connect(self.select_source); self.ingest_button.clicked.connect(self.start_ingestion)
        row.addLayout(source_text, 1); row.addWidget(self.select_source_button); row.addWidget(self.ingest_button)
        self.source_notice = QLabel(SOURCE_NOTICE); self.source_notice.setWordWrap(True)
        self.progress_label, self.progress = QLabel("Aguardando indexação"), QProgressBar()
        self.progress.hide()
        column.addLayout(row); column.addWidget(self.source_notice); column.addWidget(self.progress_label); column.addWidget(self.progress)
        box.setLayout(column); layout.addWidget(box)

        box, column, row = QGroupBox("Pesquisar na biblioteca"), QVBoxLayout(), QHBoxLayout()
        self.query = QLineEdit(); self.query.setAccessibleName("Palavras da pesquisa")
        self.query.setPlaceholderText("Digite palavras presentes nos seus documentos")
        self.query.returnPressed.connect(lambda: self.search(reset=True))
        self.clear_search_button, self.search_button = QToolButton(), QPushButton("Pesquisar")
        self.clear_search_button.setText("Limpar"); self.clear_search_button.setAccessibleName("Limpar pesquisa")
        self.clear_search_button.clicked.connect(self.clear_search); self.search_button.clicked.connect(lambda: self.search(reset=True))
        row.addWidget(self.query, 1); row.addWidget(self.clear_search_button); row.addWidget(self.search_button); column.addLayout(row)
        self.filters_button = QToolButton(); self.filters_button.setText("Filtros"); self.filters_button.setCheckable(True)
        self.filters_button.setArrowType(Qt.ArrowType.RightArrow); self.filters_button.toggled.connect(self._toggle_filters)
        column.addWidget(self.filters_button)
        self.filters_panel, filters = QWidget(), QFormLayout()
        self.filters_panel.setLayout(filters)
        self.extension, self.media_type, self.root_filter, self.path_prefix = QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()
        self.limit = QSpinBox(); self.limit.setRange(1, 100); self.limit.setValue(20)
        for label, widget in (("Extensão", self.extension), ("Tipo/MIME", self.media_type), ("Raiz", self.root_filter),
                              ("Prefixo", self.path_prefix), ("Limite por página", self.limit)):
            filters.addRow(label, widget)
        self.filters_panel.hide(); column.addWidget(self.filters_panel); box.setLayout(column); layout.addWidget(box)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        left, left_layout = QWidget(), QVBoxLayout()
        left.setLayout(left_layout); self.results_state = QLabel(EMPTY_NO_SEARCH)
        self.results = QTreeWidget(); self.results.setHeaderLabels(("Documento", "Tipo", "Localização", "Conteúdo encontrado"))
        self.results.setRootIsDecorated(False); self.results.setAlternatingRowColors(True)
        self.results.itemSelectionChanged.connect(self.show_details)
        header = self.results.header()
        for section in (0, 1): header.setSectionResizeMode(section, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive); header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        pagination = QHBoxLayout(); self.previous_button, self.next_button = QPushButton("Anterior"), QPushButton("Próxima")
        self.page_label = QLabel("0 resultados"); self.previous_button.clicked.connect(self.previous_page); self.next_button.clicked.connect(self.next_page)
        pagination.addWidget(self.previous_button); pagination.addWidget(self.page_label, 1); pagination.addWidget(self.next_button)
        left_layout.addWidget(self.results_state); left_layout.addWidget(self.results, 1); left_layout.addLayout(pagination)
        self.splitter.addWidget(left)

        self.tabs, details_panel, details_layout = QTabWidget(), QWidget(), QVBoxLayout()
        details_panel.setLayout(details_layout); details_layout.addWidget(QLabel("Detalhes principais"))
        self.details = QTextEdit(); self.details.setReadOnly(True); self.details.setPlainText(EMPTY_NO_SELECTION)
        self.technical_button = QToolButton(); self.technical_button.setText("Detalhes técnicos"); self.technical_button.setCheckable(True)
        self.technical_button.setArrowType(Qt.ArrowType.RightArrow); self.technical_button.toggled.connect(self._toggle_technical)
        self.technical_details = QTextEdit(); self.technical_details.setReadOnly(True); self.technical_details.hide()
        details_layout.addWidget(self.details, 1); details_layout.addWidget(self.technical_button); details_layout.addWidget(self.technical_details, 1)
        self.tabs.addTab(details_panel, "Detalhes")
        self.report_views: dict[str, QTextEdit] = {}
        for key, title, empty in (("ingestion", "Indexação", EMPTY_NO_DOCUMENTS),
                                  ("failure", "Problemas", EMPTY_NO_FAILURES), ("duplicate", "Duplicatas", EMPTY_NO_DUPLICATES)):
            view = QTextEdit(); view.setReadOnly(True); view.setPlainText(empty); self.report_views[key] = view; self.tabs.addTab(view, title)
        panel, panel_layout = QWidget(), QVBoxLayout(); panel.setLayout(panel_layout)
        self.refresh_reports_button = QPushButton("Atualizar relatórios"); self.refresh_reports_button.clicked.connect(self.refresh_reports)
        panel_layout.addWidget(self.tabs); panel_layout.addWidget(self.refresh_reports_button); self.splitter.addWidget(panel)
        self.splitter.setStretchFactor(0, 3); self.splitter.setStretchFactor(1, 2); self.splitter.setSizes((660, 440))
        layout.addWidget(self.splitter, 1); self._update_controls(False)

    def _toggle_filters(self, shown: bool) -> None:
        self.filters_panel.setVisible(shown); self.filters_button.setArrowType(Qt.ArrowType.DownArrow if shown else Qt.ArrowType.RightArrow)

    def _toggle_technical(self, shown: bool) -> None:
        self.technical_details.setVisible(shown); self.technical_button.setArrowType(Qt.ArrowType.DownArrow if shown else Qt.ArrowType.RightArrow)

    def _update_controls(self, valid: bool) -> None:
        active = self._thread is not None
        self.ingest_button.setEnabled(valid and self.source is not None and not active)
        self.search_button.setEnabled(valid and not active)
        for widget in (self.select_source_button, self.select_database_button, self.default_database_button, self.filters_button):
            widget.setEnabled(not active)
        self.refresh_reports_button.setEnabled(valid and not active)
        self.previous_button.setEnabled(valid and self.offset > 0 and not active)
        more = bool(self.page and self.offset + self.page.limit < self.page.total_matches)
        self.next_button.setEnabled(valid and more and not active)

    def _validate_database(self, path: Path, *, create: bool) -> bool:
        try:
            if create: path.parent.mkdir(parents=True, exist_ok=True)
            if self.facade.validate_database(str(path), create=create).schema_version > 3: raise ValueError
        except Exception:
            self.database_state.setText("Biblioteca inválida ou incompatível"); self._update_controls(False); return False
        self.database = path; self.database_label.setText(path.name); self.database_label.setToolTip(str(path))
        self.database_state.setText("Biblioteca pronta"); self._update_controls(True); return True

    @Slot()
    def use_default_database(self) -> None: self._validate_database(self.default_database, create=not self.default_database.is_file())

    @Slot()
    def select_database(self) -> None:
        chosen, _ = QFileDialog.getSaveFileName(self, "Selecionar biblioteca local", str(self.database), "Biblioteca local (*.sqlite3 *.sqlite);;Todos os arquivos (*)")
        if chosen:
            path = Path(chosen); self._validate_database(path, create=not path.is_file())

    @Slot()
    def select_source(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Adicionar pasta de documentos")
        if chosen:
            self.source = Path(chosen); self.source_label.setText(self.source.name or str(self.source)); self.source_label.setToolTip(str(self.source))
            self.source_path_label.setText(_abbreviated_path(self.source)); self.source_path_label.setToolTip(str(self.source))
            self.select_source_button.setText("Alterar pasta…"); self.progress_label.setText(EMPTY_NO_DOCUMENTS); self._update_controls(True)

    def _confirm_ingestion(self) -> bool:
        if self.source is None: return False
        dialog = QMessageBox(self); dialog.setWindowTitle("Confirmar indexação"); dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setText(f"Indexar a pasta \"{self.source.name or self.source}\"?")
        dialog.setInformativeText(f"Pasta: {self.source}\n\n{SOURCE_NOTICE}\n\nO CKO iniciará a leitura, extração e indexação local.")
        cancel = dialog.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        start = dialog.addButton("Iniciar indexação", QMessageBox.ButtonRole.AcceptRole)
        dialog.setDefaultButton(start); dialog.setEscapeButton(cancel)
        getattr(dialog, "exec")()
        return dialog.clickedButton() is start

    @Slot()
    def start_ingestion(self) -> None:
        if self._thread is not None or self.source is None or not self._confirm_ingestion(): return
        request = IngestRequest(str(self.source), str(self.database)); thread, worker = QThread(self), IngestionWorker(self.facade, request)
        worker.moveToThread(thread); thread.started.connect(worker.run); worker.progress.connect(self.on_progress)
        worker.succeeded.connect(self.ingestion_succeeded); worker.failed.connect(self.ingestion_failed)
        worker.succeeded.connect(worker.deleteLater); worker.failed.connect(worker.deleteLater)
        worker.succeeded.connect(thread.quit); worker.failed.connect(thread.quit)
        thread.finished.connect(thread.deleteLater); thread.finished.connect(self.thread_finished)
        self._thread, self._worker = thread, worker; self.progress.show(); self.progress.setRange(0, 0)
        self.progress_label.setText("Iniciando indexação"); self._update_controls(True); thread.start()

    @Slot(object)
    def on_progress(self, event: ProgressEvent) -> None:
        self.progress_label.setText(PROGRESS_TEXT[event.stage] + (f" ({event.count})" if event.count is not None else ""))

    @Slot(object)
    def ingestion_succeeded(self, result: object) -> None:
        self.progress.setRange(0, 100); self.progress.setValue(100); self.progress.hide()
        self.progress_label.setText("Indexação concluída. Sua biblioteca está pronta para pesquisa.")
        self.report_views["ingestion"].setPlainText(_ingestion_text(getattr(result, "report", result)))

    @Slot(str)
    def ingestion_failed(self, message: str) -> None:
        self.progress.setRange(0, 100); self.progress.setValue(0); self.progress.hide(); self.progress_label.setText(message)

    @Slot()
    def thread_finished(self) -> None:
        self._thread = self._worker = None; self._update_controls(True); self.refresh_reports(); self.query.setFocus()

    def _text_or_none(self, widget: QLineEdit) -> str | None: return widget.text().strip() or None

    @Slot()
    def clear_search(self) -> None:
        self.query.clear(); self.offset = 0; self.page = None; self.results.clear(); self.results_state.setText(EMPTY_NO_SEARCH)
        self.page_label.setText("0 resultados"); self.details.setPlainText(EMPTY_NO_SELECTION); self.technical_details.clear(); self.query.setFocus(); self._update_controls(True)

    @Slot()
    def search(self, *, reset: bool = True) -> None:
        if reset: self.offset = 0
        request = SearchRequest(self.query.text(), str(self.database), self.limit.value(), self._text_or_none(self.extension),
            self._text_or_none(self.media_type), self._text_or_none(self.root_filter), self._text_or_none(self.path_prefix), None, self.offset)
        try: self.page = self.facade.search(request)
        except Exception: self._show_error("Não foi possível realizar a busca."); return
        self.results.clear()
        for result in self.page.results:
            item = QTreeWidgetItem((result.title or Path(result.path).name, friendly_type(result.media_type, result.extension), result.path, result.snippet))
            item.setData(0, Qt.ItemDataRole.UserRole, result.sha256); item.setToolTip(0, item.text(0)); item.setToolTip(1, result.media_type)
            item.setToolTip(2, f"{result.root}\n{result.path}" if result.root else result.path); item.setToolTip(3, result.snippet); self.results.addTopLevelItem(item)
        total = self.page.total_matches; self.results_state.setText(EMPTY_NO_RESULTS if not total else f"{total} resultado(s) encontrado(s)")
        self.page_label.setText("0 resultados" if not total else f"{self.offset + 1}–{self.offset + len(self.page.results)} de {total}")
        self.details.setPlainText(EMPTY_NO_SELECTION); self.technical_details.clear(); self._update_controls(True)

    @Slot()
    def previous_page(self) -> None: self.offset = max(0, self.offset - self.limit.value()); self.search(reset=False)

    @Slot()
    def next_page(self) -> None:
        if self.page and self.offset + self.page.limit < self.page.total_matches:
            self.offset += self.page.limit; self.search(reset=False)

    @Slot()
    def show_details(self) -> None:
        selected = self.results.selectedItems()
        if not selected: self.details.setPlainText(EMPTY_NO_SELECTION); self.technical_details.clear(); return
        try: bundle = self.facade.get_document_details(selected[0].data(0, Qt.ItemDataRole.UserRole), str(self.database))
        except Exception: self.details.setPlainText("Não foi possível consultar os detalhes."); self.technical_details.clear(); return
        document = bundle.document; origin = document.origins[0] if document.origins else None
        primary = [f"Nome: {Path(origin.relative_path).name if origin else selected[0].text(0)}",
            f"Tipo: {friendly_type(document.media_type, document.extension)}", f"Tamanho: {_format_size(document.size_bytes)}",
            f"Localização: {origin.relative_path if origin else 'Não disponível'}", f"Origem: {origin.root if origin else 'Não disponível'}",
            f"Status de indexação: {'Indexado' if document.indexing.indexed else 'Não indexado'}"]
        if document.indexing.indexed_at: primary.append(f"Data de indexação: {document.indexing.indexed_at}")
        if document.duplicate: primary.append(f"Duplicidade: este documento aparece em {len(document.duplicate.origins)} locais")
        self.details.setPlainText("\n".join(primary))
        technical = [f"SHA-256: {document.sha256}", f"MIME: {document.media_type}", f"Extensão: {document.extension}",
                     f"Indexado em: {document.indexing.indexed_at or 'Não disponível'}"]
        if origin: technical.append(f"mtime_ns: {origin.mtime_ns}")
        if document.extraction: technical.extend((f"Extractor: {document.extraction.extractor}",
            f"Extractor version: {document.extraction.extractor_version}", f"Extração observada em: {document.extraction.observed_at}",
            f"Status da extração: {document.extraction.status}"))
        if document.issues or bundle.unresolved_historical_issues: technical.append("Issues:\n" + _render(tuple(document.issues) + tuple(bundle.unresolved_historical_issues)))
        self.technical_details.setPlainText("\n".join(technical))

    @Slot()
    def refresh_reports(self) -> None:
        try:
            if self.source is not None:
                self.report_views["ingestion"].setPlainText(_ingestion_text(self.facade.get_ingestion_report(str(self.database), str(self.source))))
            failure = self.facade.get_failure_report(str(self.database), str(self.source) if self.source else None)
            duplicate = self.facade.get_duplicate_report(str(self.database), str(self.source) if self.source else None)
        except Exception:
            self.report_views["failure"].setPlainText("Relatórios indisponíveis."); self.report_views["duplicate"].setPlainText("Relatórios indisponíveis.")
        else:
            self.report_views["failure"].setPlainText(_failure_text(failure)); self.report_views["duplicate"].setPlainText(_duplicate_text(duplicate))

    def _show_error(self, message: str) -> None: QMessageBox.warning(self, "CKO Local Knowledge Finder", message)

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._thread is not None:
            QMessageBox.information(self, "Indexação em andamento", "A indexação está em andamento.\nAguarde a conclusão antes de fechar a aplicação.")
            event.ignore(); return
        event.accept()
