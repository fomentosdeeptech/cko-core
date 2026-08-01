from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from cko.kb.database import KnowledgeBase
from cko.scanner.inventory import run_inventory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path.home() / "Downloads"
DEFAULT_DATABASE = PROJECT_ROOT / "runtime" / "database" / "cko.db"
DEFAULT_REPORT = PROJECT_ROOT / "logs" / "spr004_inventory.json"
DEFAULT_DUPLICATES = PROJECT_ROOT / "logs" / "duplicates.json"
DEFAULT_GRAPH = PROJECT_ROOT / "runtime" / "graph" / "document_graph.json"
DEFAULT_CHECKPOINT = PROJECT_ROOT / "runtime" / "checkpoints" / "spr004_checkpoint.json"
DEFAULT_LOG = PROJECT_ROOT / "logs" / "SPR004.log"
DEFAULT_SUMMARY = PROJECT_ROOT / "docs" / "sprint" / "SPR004_REPORT.md"


def configure_logging() -> None:
    DEFAULT_LOG.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(DEFAULT_LOG, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def write_summary(stats: dict[str, object], source: Path, dry_run: bool) -> None:
    DEFAULT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    content = f"""# SPR-004 — Relatório de Execução

## Fonte analisada

`{source}`

## Modo

`{"DRY-RUN" if dry_run else "GRAVAÇÃO"}`

## Resultado

- Encontrados: {stats.get("found", 0)}
- Processados: {stats.get("processed", 0)}
- Ignorados: {stats.get("ignored", 0)}
- Erros: {stats.get("errors", 0)}
- Salvos: {stats.get("saved", 0)}
- Retomados de checkpoint: {stats.get("resumed", 0)}
- Tamanho total: {stats.get("total_size_bytes", 0)} bytes
- Tempo: {stats.get("elapsed_seconds", 0)} segundos

## Garantias

Nenhum arquivo foi movido, renomeado ou excluído.
"""
    DEFAULT_SUMMARY.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CKO Core — SPR-004")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--batch-size", type=int, default=250)
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Grava os metadados no SQLite. Sem esta opção, executa em DRY-RUN.",
    )
    parser.add_argument(
        "--reset-checkpoint",
        action="store_true",
        help="Apaga o checkpoint antes de iniciar uma nova execução.",
    )
    return parser


def main() -> None:
    configure_logging()
    args = build_parser().parse_args()

    if args.reset_checkpoint and DEFAULT_CHECKPOINT.exists():
        DEFAULT_CHECKPOINT.unlink()

    database = KnowledgeBase(args.database)
    dry_run = not args.commit

    stats = run_inventory(
        source=args.source,
        database=database,
        batch_size=args.batch_size,
        dry_run=dry_run,
        report_path=DEFAULT_REPORT,
        duplicates_path=DEFAULT_DUPLICATES,
        graph_path=DEFAULT_GRAPH,
        checkpoint_path=DEFAULT_CHECKPOINT,
    )

    write_summary(stats, args.source, dry_run)

    print("\n========== RESULTADO SPR-004 ==========")
    for key, value in stats.items():
        print(f"{key:18}: {value}")
    print(f"relatório         : {DEFAULT_REPORT}")
    print(f"checkpoint        : {DEFAULT_CHECKPOINT}")
    print(f"resumo            : {DEFAULT_SUMMARY}")
    if not dry_run:
        print(f"duplicados        : {DEFAULT_DUPLICATES}")
        print(f"grafo             : {DEFAULT_GRAPH}")
        print(f"banco             : {args.database}")
    print("Nenhum arquivo foi movido, renomeado ou excluído.")
    print("=======================================\n")


if __name__ == "__main__":
    main()
