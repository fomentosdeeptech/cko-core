from pathlib import Path
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from cko.utils.file_utils import (
    arquivo_temporario,
    esperar_arquivo,
    metadados
)


class DownloadHandler(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        arquivo = Path(event.src_path)

        if arquivo_temporario(arquivo):
            return

        if not esperar_arquivo(arquivo):
            return

        info = metadados(arquivo)

        print("\n========== NOVO DOCUMENTO ==========")

        for chave, valor in info.items():

            print(f"{chave:10}: {valor}")

        print("====================================\n")


def iniciar_scanner(pasta):

    observer = Observer()

    observer.schedule(
        DownloadHandler(),
        str(pasta),
        recursive=False
    )

    observer.start()

    print(f"Monitorando: {pasta}")

    try:

        while True:

            time.sleep(1)

    except KeyboardInterrupt:

        observer.stop()

    observer.join()