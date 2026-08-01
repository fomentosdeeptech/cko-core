"""Logging JSON consistente para SDK, aplicações e adaptadores."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import IO


class JsonFormatter(logging.Formatter):
    """Formata cada registro como um objeto JSON UTF-8."""

    def format(self, record: logging.LogRecord) -> str:
        """Serializa campos estáveis e contexto opcional do registro."""
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        event = getattr(record, "event", None)
        context = getattr(record, "context", None)
        if event is not None:
            payload["event"] = event
        if context is not None:
            payload["context"] = context
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(
    level: int | str = logging.INFO,
    *,
    stream: IO[str] | None = None,
    logger_name: str = "cko",
) -> logging.Logger:
    """Configura de forma idempotente o logger raiz do namespace CKO."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger.handlers.clear()
    logger.addHandler(handler)
    return logger


def get_logger(name: str) -> logging.Logger:
    """Obtém um logger subordinado ao namespace oficial ``cko``."""
    normalized = name.strip().strip(".")
    if not normalized:
        raise ValueError("name não pode ser vazio")
    return logging.getLogger(f"cko.{normalized}")

