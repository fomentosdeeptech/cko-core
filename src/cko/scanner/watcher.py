from __future__ import annotations

import logging
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from cko.kb.database import KnowledgeBase
from cko.metadata.file_metadata import (
    collect_metadata,
    is_temporary,
    wait_until_stable,
)


LOGGER = logging.getLogger("cko.watcher")


class DownloadHandler(FileSystemEventHandler):
    def __init__(
        self,
        database: KnowledgeBase,
        calculate_hash: bool = True,
        dry_run: bool = True,
    ) -> None:
        self.database = database
        self.calculate_hash = calculate_hash
        self.dry_run = dry_run

    def on_created(self, event) -> None:
        if event.is_directory:
            return

        path = Path(event.src_path)

        if is_temporary(path):
            print(f"[IGNORADO] temporário: {path.name}")
            return

        if not wait_until_stable(path):
            print(f"[PENDENTE] arquivo não estabilizou: {path.name}")
            return

        try:
            metadata = collect_metadata(path, calculate_hash=self.calculate_hash)

            print("\n========== NOVO DOCUMENTO ==========")
            print(f"nome      : {metadata.name}")
            print(f"extensão  : {metadata.extension}")
            print(f"tamanho   : {metadata.size_bytes} bytes")
            print(f"mime      : {metadata.mime_type}")
            print(f"sha256    : {metadata.sha256 or 'não calculado'}")
            print(f"modo      : {'DRY-RUN' if self.dry_run else 'GRAVAÇÃO'}")
            print("====================================\n")

            if not self.dry_run:
                self.database.upsert(metadata)

        except (PermissionError, FileNotFoundError, OSError) as exc:
            LOGGER.exception("Falha ao processar %s: %s", path, exc)


def start_watcher(
    source: Path,
    database: KnowledgeBase,
    calculate_hash: bool = True,
    dry_run: bool = True,
) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {source}")

    database.initialize()
    observer = Observer()
    observer.schedule(
        DownloadHandler(
            database=database,
            calculate_hash=calculate_hash,
            dry_run=dry_run,
        ),
        str(source),
        recursive=False,
    )
    observer.start()

    print(f"Monitorando: {source}")
    print(f"Modo: {'DRY-RUN' if dry_run else 'GRAVAÇÃO'}")
    print("Pressione Ctrl+C para encerrar.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
