from __future__ import annotations

import hashlib
import mimetypes
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


IGNORED_SUFFIXES = {
    ".tmp", ".crdownload", ".part", ".download", ".lock",
}

IGNORED_PREFIXES = (
    "~$", "~WRD", ".~lock.", ".",
)


@dataclass(frozen=True)
class FileMetadata:
    path: str
    name: str
    extension: str
    size_bytes: int
    created_at: str
    modified_at: str
    mime_type: str
    sha256: str
    parent_folder: str
    depth: int
    category: str


def is_temporary(path: Path) -> bool:
    name = path.name
    return (
        path.suffix.lower() in IGNORED_SUFFIXES
        or any(name.startswith(prefix) for prefix in IGNORED_PREFIXES)
    )


def calculate_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iso_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def classify_by_extension(path: Path) -> str:
    ext = path.suffix.lower()

    groups = {
        "PDF": {".pdf"},
        "Imagem": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp"},
        "Planilha": {".xls", ".xlsx", ".xlsm", ".ods", ".csv"},
        "Apresentação": {".ppt", ".pptx", ".odp"},
        "Documento": {".doc", ".docx", ".odt", ".rtf"},
        "Texto": {".txt", ".md"},
        "Código": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".cs", ".go", ".rs", ".html", ".css", ".json", ".yaml", ".yml", ".toml"},
        "Compactado": {".zip", ".rar", ".7z", ".tar", ".gz"},
        "Áudio": {".mp3", ".wav", ".m4a", ".flac", ".aac"},
        "Vídeo": {".mp4", ".avi", ".mov", ".mkv", ".wmv"},
    }

    for category, extensions in groups.items():
        if ext in extensions:
            return category

    return "Outros"


def collect_metadata(path: Path, source_root: Path) -> FileMetadata:
    stat = path.stat()
    mime_type, _ = mimetypes.guess_type(path.name)

    try:
        relative = path.resolve().relative_to(source_root.resolve())
        depth = max(0, len(relative.parts) - 1)
    except ValueError:
        depth = 0

    return FileMetadata(
        path=str(path.resolve()),
        name=path.name,
        extension=path.suffix.lower(),
        size_bytes=stat.st_size,
        created_at=_iso_timestamp(stat.st_ctime),
        modified_at=_iso_timestamp(stat.st_mtime),
        mime_type=mime_type or "application/octet-stream",
        sha256=calculate_sha256(path),
        parent_folder=str(path.parent.resolve()),
        depth=depth,
        category=classify_by_extension(path),
    )
