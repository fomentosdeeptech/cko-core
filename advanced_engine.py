#!/usr/bin/env python3
"""Infraestrutura avançada da SPR-007B.

Este módulo implementa uma infraestrutura mínima, segura e modular para a
entrega SPR-007B Pacote 1, sem executar leitura documental, sem classificar
arquivos e sem gravar no banco canônico.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class PipelineStage:
    """Representa um estágio do pipeline."""

    name: str
    status: str = "not_executed"
    executed: bool = False


@dataclass(slots=True)
class EngineConfig:
    """Configuração segura usada pela engine."""

    canonical_database_path: str
    knowledge_database_path: str
    allow_canonical_writes: bool = False
    todo: str = "TODO SPR-007B PACKAGE 2"


class StructuredLogger:
    """Logger estruturado em formato JSON Lines."""

    def __init__(self, log_path: Path, component: str) -> None:
        self.log_path = log_path
        self.component = component
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.log_path.open("a", encoding="utf-8")

    def _write(self, level: str, event: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "component": self.component,
            "event": event,
            "message": message,
            "context": context or {},
        }
        self._handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        self._handle.write("\n")
        self._handle.flush()

    def info(self, event: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._write("INFO", event, message, context)

    def warning(self, event: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._write("WARNING", event, message, context)

    def error(self, event: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._write("ERROR", event, message, context)

    def close(self) -> None:
        self._handle.close()


class Environment:
    """Resumo do ambiente operacional."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()
        self.runtime_dir = self.project_root / "runtime"
        self.database_dir = self.runtime_dir / "database"
        self.logs_dir = self.project_root / "logs"
        self.reports_dir = self.project_root / "reports"
        self.canonical_database_path = self.database_dir / "cko_canonical.db"
        self.knowledge_database_path = self.database_dir / "cko_knowledge.db"
        self.config_path = self.project_root / "engine_config.json"

    def ensure_directories(self) -> None:
        for path in (self.runtime_dir, self.database_dir, self.logs_dir, self.reports_dir):
            path.mkdir(parents=True, exist_ok=True)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "project_root": str(self.project_root),
            "runtime_dir": str(self.runtime_dir),
            "database_dir": str(self.database_dir),
            "logs_dir": str(self.logs_dir),
            "reports_dir": str(self.reports_dir),
            "canonical_database_path": str(self.canonical_database_path),
            "knowledge_database_path": str(self.knowledge_database_path),
            "config_path": str(self.config_path),
        }


class Bootstrap:
    """Bootstrap da infraestrutura da SPR-007B."""

    def __init__(self, environment: Environment, logger: StructuredLogger) -> None:
        self.environment = environment
        self.logger = logger
        self.python_version: Optional[str] = None
        self.sqlite_version: Optional[str] = None
        self.canonical_validation: Dict[str, Any] = {}
        self.lateral_validation: Dict[str, Any] = {}
        self.components: List[str] = []

    def _resolve_python(self) -> Optional[tuple[str, List[str]]]:
        python3_13 = self._probe_path("python3.13.exe")
        if python3_13:
            return (python3_13, [])
        python = self._probe_path("python.exe")
        if python:
            return (python, [])
        if self._probe_py_launcher():
            return ("py", ["-3.13"])
        return None

    def _probe_path(self, name: str) -> Optional[str]:
        if os.name != "nt":
            return None
        return shutil.which(name)

    def _probe_py_launcher(self) -> bool:
        if os.name != "nt":
            return False
        return shutil.which("py") is not None or shutil.which("py.exe") is not None

    def validate_python(self) -> Optional[str]:
        resolved_python = self._resolve_python()
        if resolved_python is None:
            self.logger.error("bootstrap.python_missing", "Python 3.13 não encontrado.")
            return None
        executable, extra_args = resolved_python
        version_output = self._run_command(executable, [*extra_args, "--version"])
        if version_output is None:
            self.logger.error("bootstrap.python_version_failed", "Falha ao verificar a versão do Python.")
            return None
        version_text = version_output.strip().split()[-1]
        if version_text.startswith("3.13"):
            self.python_version = version_text
            self.logger.info("bootstrap.python_validated", "Python 3.13 validado.", {"version": version_text})
            return executable
        self.logger.error("bootstrap.python_version_invalid", "Python 3.13 não foi encontrado.", {"version": version_text})
        return None

    def _run_command(self, executable: str, arguments: List[str]) -> Optional[str]:
        try:
            proc = subprocess.run([executable, *arguments], capture_output=True, text=True, check=False)
        except FileNotFoundError:
            return None
        if proc.returncode != 0:
            return None
        return proc.stdout.strip()

    def validate_environment(self) -> bool:
        self.environment.ensure_directories()
        self.logger.info("bootstrap.directories_ready", "Diretórios de runtime, database, logs e reports preparados.")
        for directory in (self.environment.runtime_dir, self.environment.database_dir, self.environment.logs_dir, self.environment.reports_dir):
            try:
                test_path = directory / ".write_test"
                with test_path.open("w", encoding="utf-8") as handle:
                    handle.write("ok")
                test_path.unlink(missing_ok=True)
            except OSError as exc:
                self.logger.error("bootstrap.permission_error", "Falha de permissão detectada.", {"path": str(directory), "error": str(exc)})
                return False
        self.logger.info("bootstrap.permissions_ok", "Permissões de escrita validadas.")
        return True

    def validate_canonical_database(self) -> bool:
        path = self.environment.canonical_database_path
        if not path.exists():
            self.logger.error("bootstrap.canonical_missing", "Banco canônico não encontrado.", {"path": str(path)})
            return False
        if not path.is_file():
            self.logger.error("bootstrap.canonical_not_file", "Banco canônico não é um arquivo regular.", {"path": str(path)})
            return False
        try:
            size = path.stat().st_size
        except OSError as exc:
            self.logger.error("bootstrap.canonical_stat_failed", "Falha ao obter status do banco canônico.", {"path": str(path), "error": str(exc)})
            return False
        self.canonical_validation = {"path": str(path), "size_bytes": size}
        try:
            uri = f"file:{path}?mode=ro&immutable=1"
            connection = sqlite3.connect(uri, uri=True)
        except sqlite3.Error as exc:
            self.logger.error("bootstrap.canonical_connect_failed", "Falha ao abrir o banco canônico somente leitura.", {"error": str(exc)})
            return False
        try:
            connection.execute("PRAGMA query_only=ON")
            query_only = connection.execute("PRAGMA query_only").fetchone()
            if query_only is None or int(query_only[0]) != 1:
                self.logger.error("bootstrap.query_only_failed", "PRAGMA query_only não ficou habilitado.")
                return False
            self.canonical_validation["query_only"] = int(query_only[0])
            self.canonical_validation["quick_check"] = connection.execute("PRAGMA quick_check").fetchone()[0]
            self.canonical_validation["sqlite_version"] = connection.execute("SELECT sqlite_version()").fetchone()[0]
            self.canonical_validation["schema_version"] = connection.execute("PRAGMA user_version").fetchone()[0]
            self.canonical_validation["application_id"] = connection.execute("PRAGMA application_id").fetchone()[0]
            self.canonical_validation["page_count"] = connection.execute("PRAGMA page_count").fetchone()[0]
            self.canonical_validation["page_size"] = connection.execute("PRAGMA page_size").fetchone()[0]
            self.canonical_validation["journal_mode"] = connection.execute("PRAGMA journal_mode").fetchone()[0]
            self.logger.info("bootstrap.canonical_validated", "Banco canônico validado em modo somente leitura.", self.canonical_validation)
            return True
        except sqlite3.Error as exc:
            self.logger.error("bootstrap.canonical_validation_failed", "Falha na validação do banco canônico.", {"error": str(exc)})
            return False
        finally:
            connection.close()

    def load_config(self) -> EngineConfig:
        if not self.environment.config_path.exists():
            self.logger.info("bootstrap.config_missing", "engine_config.json não encontrado. Usando configuração interna segura.", {"todo": "TODO SPR-007B PACKAGE 2"})
            return EngineConfig(
                canonical_database_path=str(self.environment.canonical_database_path),
                knowledge_database_path=str(self.environment.knowledge_database_path),
            )
        try:
            payload = json.loads(self.environment.config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.logger.error("bootstrap.config_invalid_json", "engine_config.json contém JSON inválido.", {"error": str(exc)})
            raise ValueError("Configuração inválida") from exc
        if not isinstance(payload, dict):
            self.logger.error("bootstrap.config_invalid_shape", "engine_config.json deve ser um objeto JSON.")
            raise ValueError("Configuração inválida")
        canonical_path = payload.get("canonical_database_path")
        knowledge_path = payload.get("knowledge_database_path")
        allow_canonical_writes = payload.get("allow_canonical_writes", False)
        if not isinstance(canonical_path, str) or not canonical_path.strip():
            raise ValueError("canonical_database_path obrigatório")
        if not isinstance(knowledge_path, str) or not knowledge_path.strip():
            raise ValueError("knowledge_database_path obrigatório")
        if not isinstance(allow_canonical_writes, bool):
            raise ValueError("allow_canonical_writes deve ser booleano")
        if allow_canonical_writes:
            self.logger.error("bootstrap.config_forbids_canonical_write", "A configuração não pode permitir escrita no banco canônico.")
            raise ValueError("Configuração inválida")
        if Path(canonical_path).resolve() == Path(knowledge_path).resolve():
            self.logger.error("bootstrap.config_duplicate_paths", "Os caminhos do banco canônico e lateral não podem ser iguais.")
            raise ValueError("Configuração inválida")
        return EngineConfig(
            canonical_database_path=canonical_path,
            knowledge_database_path=knowledge_path,
            allow_canonical_writes=False,
            todo="TODO SPR-007B PACKAGE 2",
        )

    def run(self) -> Dict[str, Any]:
        self.logger.info("bootstrap.start", "Inicialização da infraestrutura SPR-007B iniciada.")
        self.components = ["Bootstrap", "StructuredLogger", "Environment", "Database", "Pipeline", "Scanner", "Cache", "ReportWriter"]
        python_executable = self.validate_python()
        if python_executable is None:
            self.logger.error("bootstrap.abort", "Bootstrap abortado por ausência de Python 3.13.")
            return {"status": "failed", "reason": "python_missing"}
        if not self.validate_environment():
            self.logger.error("bootstrap.abort", "Bootstrap abortado por falha de ambiente.")
            return {"status": "failed", "reason": "environment_error"}
        if not self.validate_canonical_database():
            self.logger.error("bootstrap.abort", "Bootstrap abortado por falha do banco canônico.")
            return {"status": "failed", "reason": "canonical_error"}
        config = self.load_config()
        database = Database(self.environment, config, self.logger)
        database.initialize_lateral()
        pipeline = Pipeline(self.logger)
        scanner = Scanner(self.logger)
        cache = Cache(self.logger)
        report_writer = ReportWriter(self.logger)
        self.lateral_validation = database.validation_summary()
        self.sqlite_version = self.canonical_validation.get("sqlite_version")
        result = {
            "status": "succeeded",
            "components": self.components,
            "environment": self.environment.as_dict(),
            "config": {
                "canonical_database_path": config.canonical_database_path,
                "knowledge_database_path": config.knowledge_database_path,
                "allow_canonical_writes": config.allow_canonical_writes,
                "todo": config.todo,
            },
            "python_version": self.python_version,
            "sqlite_version": self.sqlite_version,
            "canonical_validation": self.canonical_validation,
            "lateral_validation": self.lateral_validation,
            "pipeline": pipeline.as_dict(),
            "scanner": scanner.as_dict(),
            "cache": cache.as_dict(),
            "artifacts": {
                "bootstrap_log": str(self.environment.logs_dir / "SPR007B_BOOTSTRAP.log"),
                "engine_log": str(self.environment.logs_dir / "SPR007B_ENGINE.log"),
                "report_md": str(self.environment.reports_dir / "SPR007B_ADVANCED_REPORT.md"),
                "report_json": str(self.environment.reports_dir / "SPR007B_ADVANCED_REPORT.json"),
            },
        }
        self.logger.info("bootstrap.success", "Infraestrutura inicializada com sucesso.", result)
        return result


class Database:
    """Camada de acesso ao SQLite para o banco lateral e validação do canônico."""

    def __init__(self, environment: Environment, config: EngineConfig, logger: StructuredLogger) -> None:
        self.environment = environment
        self.config = config
        self.logger = logger
        self.connection: Optional[sqlite3.Connection] = None

    def _canonical_path(self) -> Path:
        return Path(self.config.canonical_database_path).resolve()

    def validate_canonical_readonly(self) -> Dict[str, Any]:
        path = self._canonical_path()
        connection = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
        try:
            connection.execute("PRAGMA query_only=ON")
            query_only = connection.execute("PRAGMA query_only").fetchone()[0]
            return {
                "path": str(path),
                "query_only": int(query_only),
                "quick_check": connection.execute("PRAGMA quick_check").fetchone()[0],
                "sqlite_version": connection.execute("SELECT sqlite_version()").fetchone()[0],
                "user_version": connection.execute("PRAGMA user_version").fetchone()[0],
                "application_id": connection.execute("PRAGMA application_id").fetchone()[0],
                "journal_mode": connection.execute("PRAGMA journal_mode").fetchone()[0],
            }
        finally:
            connection.close()

    def initialize_lateral(self) -> None:
        self.environment.database_dir.mkdir(parents=True, exist_ok=True)
        path = Path(self.config.knowledge_database_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        try:
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.connection.execute("BEGIN IMMEDIATE")
            self.connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS engine_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS execution_runs (
                    run_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT NOT NULL,
                    details_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    run_id TEXT PRIMARY KEY,
                    stage_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    executed INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS cache_entries (
                    cache_key TEXT PRIMARY KEY,
                    cache_value TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            self.connection.commit()
            self.logger.info("database.lateral_initialized", "Banco lateral inicializado com sucesso.", {"path": str(path)})
        except sqlite3.Error as exc:
            self.connection.rollback()
            self.logger.error("database.lateral_init_failed", "Falha na inicialização do banco lateral.", {"error": str(exc)})
            raise
        finally:
            self.connection.close()
            self.connection = None

    def validation_summary(self) -> Dict[str, Any]:
        path = Path(self.config.knowledge_database_path).resolve()
        connection = sqlite3.connect(path)
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA quick_check")
            tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
            return {
                "path": str(path),
                "sqlite_version": connection.execute("SELECT sqlite_version()").fetchone()[0],
                "schema_version": connection.execute("PRAGMA user_version").fetchone()[0],
                "application_id": connection.execute("PRAGMA application_id").fetchone()[0],
                "journal_mode": connection.execute("PRAGMA journal_mode").fetchone()[0],
                "tables": tables,
                "quick_check": connection.execute("PRAGMA quick_check").fetchone()[0],
            }
        finally:
            connection.close()


class Pipeline:
    """Pipeline mínimo com estágios registrados e não executados."""

    def __init__(self, logger: StructuredLogger) -> None:
        self.logger = logger
        self.stages: List[PipelineStage] = [
            PipelineStage("Discover"),
            PipelineStage("Read"),
            PipelineStage("Interpret"),
            PipelineStage("Entities"),
            PipelineStage("Relations"),
            PipelineStage("Reports"),
        ]

    def as_dict(self) -> Dict[str, Any]:
        self.logger.info("pipeline.assembled", "Pipeline montado com todos os estágios registrados.", {"stages": [stage.name for stage in self.stages]})
        return {
            "executed": False,
            "stages": [
                {"name": stage.name, "status": stage.status, "executed": stage.executed}
                for stage in self.stages
            ],
        }


class Scanner:
    """Scanner mínimo, instanciado sem varredura real."""

    def __init__(self, logger: StructuredLogger) -> None:
        self.logger = logger
        self.initialized = True

    def as_dict(self) -> Dict[str, Any]:
        self.logger.info("scanner.instantiated", "Scanner instanciado sem execução de varredura.")
        return {"initialized": self.initialized, "executed": False, "status": "not_executed"}


class Cache:
    """Cache interno mínimo, instanciado sem processamento documental."""

    def __init__(self, logger: StructuredLogger) -> None:
        self.logger = logger
        self.initialized = True

    def as_dict(self) -> Dict[str, Any]:
        self.logger.info("cache.instantiated", "Cache instanciado sem processamento de documentos.")
        return {"initialized": self.initialized, "executed": False, "status": "not_executed"}


class ReportWriter:
    """Escritor seguro de relatórios em Markdown e JSON."""

    def __init__(self, logger: StructuredLogger) -> None:
        self.logger = logger

    def _atomic_write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(path.parent), delete=False) as handle:
            handle.write(content)
            temp_name = handle.name
        os.replace(temp_name, path)

    def write(self, report_path_md: Path, report_path_json: Path, payload: Dict[str, Any]) -> None:
        markdown = self._render_markdown(payload)
        json_content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        self._atomic_write(report_path_md, markdown)
        self._atomic_write(report_path_json, json_content)
        self.logger.info("reports.written", "Relatórios gravados com sucesso.", {"markdown": str(report_path_md), "json": str(report_path_json)})

    def _render_markdown(self, payload: Dict[str, Any]) -> str:
        lines: List[str] = []
        lines.append("# SPR-007B Advanced Engine Report")
        lines.append("")
        lines.append(f"- Engine: {payload.get('engine_name', 'CKO SPR-007B')}")
        lines.append(f"- Version: {payload.get('version', '1.0.0')}")
        lines.append(f"- Run ID: {payload.get('run_id', 'unknown')}")
        lines.append(f"- Status: {payload.get('status', 'unknown')}")
        lines.append(f"- Started At: {payload.get('started_at', 'unknown')}")
        lines.append(f"- Finished At: {payload.get('finished_at', 'unknown')}")
        lines.append(f"- Duration Seconds: {payload.get('duration_seconds', 0)}")
        lines.append("")
        lines.append("## Validation")
        lines.append("")
        lines.append(f"- Canonical database read-only validation: {payload.get('canonical_validation', {}).get('query_only', 'n/a')}")
        lines.append(f"- Knowledge database created: {payload.get('lateral_validation', {}).get('path', 'n/a')}")
        lines.append(f"- No document reading occurred: {payload.get('no_document_reading', False)}")
        lines.append(f"- Canonical database unchanged: {payload.get('canonical_unchanged', False)}")
        lines.append("")
        lines.append("## Pipeline")
        for stage in payload.get("pipeline", {}).get("stages", []):
            lines.append(f"- {stage['name']}: {stage['status']}")
        lines.append("")
        lines.append("## Artifacts")
        for key, value in payload.get("artifacts", {}).items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CKO SPR-007B Advanced Engine")
    parser.add_argument("--project-root", default=str(Path(__file__).resolve().parent), help="Caminho da raiz operacional")
    return parser.parse_args()


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_payload(
    environment: Environment,
    bootstrap_result: Dict[str, Any],
    started_at: datetime,
    finished_at: datetime,
    status: str,
    error: Optional[str] = None,
    canonical_hash_before: Optional[str] = None,
    canonical_size_before: Optional[int] = None,
    canonical_hash_after: Optional[str] = None,
    canonical_size_after: Optional[int] = None,
) -> Dict[str, Any]:
    duration = round((finished_at - started_at).total_seconds(), 6)
    canonical_unchanged = (
        canonical_hash_before is not None
        and canonical_hash_after is not None
        and canonical_size_before is not None
        and canonical_size_after is not None
        and canonical_hash_before == canonical_hash_after
        and canonical_size_before == canonical_size_after
    )
    payload = {
        "engine_name": "CKO SPR-007B Advanced Engine",
        "version": "1.0.0",
        "run_id": str(uuid.uuid4()),
        "status": status,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": duration,
        "configuration_used": bootstrap_result.get("config", {}),
        "environment": environment.as_dict(),
        "python_version": bootstrap_result.get("python_version"),
        "sqlite_version": bootstrap_result.get("sqlite_version"),
        "canonical_validation": bootstrap_result.get("canonical_validation", {}),
        "lateral_validation": bootstrap_result.get("lateral_validation", {}),
        "components_instantiated": bootstrap_result.get("components", []),
        "pipeline": bootstrap_result.get("pipeline", {}),
        "scanner": bootstrap_result.get("scanner", {}),
        "cache": bootstrap_result.get("cache", {}),
        "no_document_reading": True,
        "canonical_unchanged": canonical_unchanged,
        "canonical_hash_before": canonical_hash_before,
        "canonical_hash_after": canonical_hash_after,
        "canonical_size_before": canonical_size_before,
        "canonical_size_after": canonical_size_after,
        "artifacts": bootstrap_result.get("artifacts", {}),
        "error": error,
    }
    return payload


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    environment = Environment(project_root)
    environment.ensure_directories()
    logger = StructuredLogger(environment.logs_dir / "SPR007B_ENGINE.log", "engine")
    started_at = datetime.now(timezone.utc)
    canonical_path = environment.canonical_database_path
    canonical_hash_before = None
    canonical_size_before = None
    if canonical_path.exists():
        canonical_hash_before = compute_sha256(canonical_path)
        canonical_size_before = canonical_path.stat().st_size
    try:
        bootstrap = Bootstrap(environment, logger)
        bootstrap_result = bootstrap.run()
        finished_at = datetime.now(timezone.utc)
        canonical_hash_after = None
        canonical_size_after = None
        if canonical_path.exists():
            canonical_hash_after = compute_sha256(canonical_path)
            canonical_size_after = canonical_path.stat().st_size
        payload = build_payload(
            environment,
            bootstrap_result,
            started_at,
            finished_at,
            bootstrap_result.get("status", "failed"),
            canonical_hash_before=canonical_hash_before,
            canonical_size_before=canonical_size_before,
            canonical_hash_after=canonical_hash_after,
            canonical_size_after=canonical_size_after,
        )
        report_writer = ReportWriter(logger)
        report_writer.write(
            environment.reports_dir / "SPR007B_ADVANCED_REPORT.md",
            environment.reports_dir / "SPR007B_ADVANCED_REPORT.json",
            payload,
        )
        logger.info("engine.completed", "Execução concluída.", payload)
        return 0 if bootstrap_result.get("status") == "succeeded" else 1
    except Exception as exc:  # pragma: no cover - tratamento global
        finished_at = datetime.now(timezone.utc)
        canonical_hash_after = None
        canonical_size_after = None
        if canonical_path.exists():
            canonical_hash_after = compute_sha256(canonical_path)
            canonical_size_after = canonical_path.stat().st_size
        error_payload = build_payload(
            environment,
            {},
            started_at,
            finished_at,
            "failed",
            str(exc),
            canonical_hash_before=canonical_hash_before,
            canonical_size_before=canonical_size_before,
            canonical_hash_after=canonical_hash_after,
            canonical_size_after=canonical_size_after,
        )
        try:
            ReportWriter(logger).write(
                environment.reports_dir / "SPR007B_ADVANCED_REPORT.md",
                environment.reports_dir / "SPR007B_ADVANCED_REPORT.json",
                error_payload,
            )
        except Exception as write_error:  # pragma: no cover
            logger.error("engine.report_failed", "Falha ao gravar relatórios.", {"error": str(write_error)})
        logger.error("engine.failed", "Execução falhou com exceção não tratada.", {"error": str(exc)})
        return 1
    finally:
        logger.close()


if __name__ == "__main__":
    sys.exit(main())
