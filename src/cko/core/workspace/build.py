"""Dependency-free deterministic wheel builder for the local CKO workspace."""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import logging
import re
import tomllib
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .manager import WorkspaceManager


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class BuildResult:
    """Description of one deterministic wheel build."""

    artifact: Path
    files: int


def _wheel_entry(name: str, content: bytes) -> tuple[zipfile.ZipInfo, bytes]:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    return info, content


def _record_line(name: str, content: bytes) -> tuple[str, str, str]:
    digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=")
    return name, f"sha256={digest.decode('ascii')}", str(len(content))


def build_wheel(
    manager: WorkspaceManager,
    output: str | Path | None = None,
) -> BuildResult:
    """Validate UTF-8 Python sources and create a deterministic pure wheel."""
    manager.create()
    manifest = manager.paths.root / "pyproject.toml"
    with manifest.open("rb") as stream:
        project = tomllib.load(stream)["project"]
    name = str(project["name"])
    version = str(project["version"])
    description = str(project.get("description", ""))
    requires_python = str(project.get("requires-python", ">=3.13"))
    normalized_name = re.sub(r"[-_.]+", "_", name)
    dist_info = f"{normalized_name}-{version}.dist-info"
    destination = (
        manager.paths.reports / "build" if output is None else Path(output).resolve()
    )
    destination.mkdir(parents=True, exist_ok=True)
    artifact = destination / f"{normalized_name}-{version}-py3-none-any.whl"
    entries: list[tuple[str, bytes]] = []
    source_root = manager.paths.root / "src"
    for source in sorted(source_root.rglob("*.py")):
        relative = source.relative_to(source_root).as_posix()
        content = source.read_bytes()
        text = content.decode("utf-8")
        compile(text, str(source), "exec")
        entries.append((relative, content))
    metadata = (
        "Metadata-Version: 2.1\n"
        f"Name: {name}\n"
        f"Version: {version}\n"
        f"Summary: {description}\n"
        f"Requires-Python: {requires_python}\n"
    ).encode("utf-8")
    wheel = (
        "Wheel-Version: 1.0\n"
        "Generator: cko-workspace\n"
        "Root-Is-Purelib: true\n"
        "Tag: py3-none-any\n"
    ).encode("utf-8")
    entries.extend((
        (f"{dist_info}/METADATA", metadata),
        (f"{dist_info}/WHEEL", wheel),
    ))
    record = io.StringIO(newline="")
    writer = csv.writer(record, lineterminator="\n")
    for entry_name, content in entries:
        writer.writerow(_record_line(entry_name, content))
    record_name = f"{dist_info}/RECORD"
    writer.writerow((record_name, "", ""))
    entries.append((record_name, record.getvalue().encode("utf-8")))
    with zipfile.ZipFile(artifact, "w") as archive:
        for entry_name, content in entries:
            archive.writestr(*_wheel_entry(entry_name, content))
    result = BuildResult(artifact=artifact, files=len(entries))
    LOGGER.info(
        "build completed",
        extra={
            "event": "build_completed",
            "context": {"artifact": str(artifact), "files": result.files},
        },
    )
    return result
