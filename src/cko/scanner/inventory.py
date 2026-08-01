from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from cko.kb.database import KnowledgeBase
from cko.metadata.file_metadata import collect_metadata, is_temporary


LOGGER = logging.getLogger("cko.inventory")


def iter_files_recursive(source: Path):
    for path in source.rglob("*"):
        if path.is_file():
            yield path


def load_checkpoint(checkpoint_path: Path) -> set[str]:
    if not checkpoint_path.exists():
        return set()

    try:
        data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        return set(data.get("processed_paths", []))
    except (json.JSONDecodeError, OSError):
        return set()


def save_checkpoint(checkpoint_path: Path, processed_paths: set[str]) -> None:
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(
        json.dumps(
            {"processed_paths": sorted(processed_paths)},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def run_inventory(
    source: Path,
    database: KnowledgeBase,
    batch_size: int = 250,
    dry_run: bool = True,
    report_path: Path | None = None,
    duplicates_path: Path | None = None,
    graph_path: Path | None = None,
    checkpoint_path: Path | None = None,
) -> dict[str, object]:
    if not source.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {source}")

    database.initialize()

    processed_paths = load_checkpoint(checkpoint_path) if checkpoint_path else set()
    started = time.monotonic()

    stats: dict[str, object] = {
        "found": 0,
        "processed": 0,
        "ignored": 0,
        "errors": 0,
        "saved": 0,
        "resumed": len(processed_paths),
        "total_size_bytes": 0,
    }

    dry_run_records: list[dict[str, object]] = []
    graph_nodes: list[dict[str, object]] = []
    graph_edges: list[dict[str, object]] = []

    for index, path in enumerate(iter_files_recursive(source), start=1):
        stats["found"] = int(stats["found"]) + 1
        resolved = str(path.resolve())

        if resolved in processed_paths:
            continue

        if is_temporary(path):
            stats["ignored"] = int(stats["ignored"]) + 1
            processed_paths.add(resolved)
            continue

        try:
            metadata = collect_metadata(path, source_root=source)
            stats["processed"] = int(stats["processed"]) + 1
            stats["total_size_bytes"] = int(stats["total_size_bytes"]) + metadata.size_bytes

            if dry_run:
                dry_run_records.append(
                    {
                        "path": metadata.path,
                        "name": metadata.name,
                        "extension": metadata.extension,
                        "size_bytes": metadata.size_bytes,
                        "mime_type": metadata.mime_type,
                        "sha256": metadata.sha256,
                        "parent_folder": metadata.parent_folder,
                        "depth": metadata.depth,
                        "category": metadata.category,
                    }
                )
            else:
                database.upsert(metadata)
                stats["saved"] = int(stats["saved"]) + 1

            graph_nodes.append(
                {
                    "id": metadata.sha256,
                    "type": "document",
                    "label": metadata.name,
                    "path": metadata.path,
                    "category": metadata.category,
                }
            )
            graph_edges.append(
                {
                    "source": metadata.sha256,
                    "target": metadata.category,
                    "relation": "classified_as",
                }
            )

            processed_paths.add(resolved)

        except (PermissionError, FileNotFoundError, OSError) as exc:
            LOGGER.exception("Falha ao processar %s: %s", path, exc)
            stats["errors"] = int(stats["errors"]) + 1

        if index % batch_size == 0:
            if checkpoint_path:
                save_checkpoint(checkpoint_path, processed_paths)

            print(
                f"[LOTE] encontrados={stats['found']} "
                f"processados={stats['processed']} "
                f"ignorados={stats['ignored']} "
                f"erros={stats['errors']} "
                f"salvos={stats['saved']}"
            )

    if checkpoint_path:
        save_checkpoint(checkpoint_path, processed_paths)

    elapsed = round(time.monotonic() - started, 2)
    stats["elapsed_seconds"] = elapsed

    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(
                {
                    "source": str(source),
                    "dry_run": dry_run,
                    "stats": stats,
                    "files": dry_run_records,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    if not dry_run:
        duplicates = database.duplicates()
        categories = database.category_counts()

        if duplicates_path:
            duplicates_path.parent.mkdir(parents=True, exist_ok=True)
            duplicates_path.write_text(
                json.dumps(duplicates, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        if graph_path:
            graph_path.parent.mkdir(parents=True, exist_ok=True)
            graph_path.write_text(
                json.dumps(
                    {
                        "nodes": graph_nodes,
                        "edges": graph_edges,
                        "categories": categories,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

    return stats
