"""Configuração de logging estruturado baseada na biblioteca padrão."""

from .structured import JsonFormatter, configure_logging, get_logger

__all__ = ["JsonFormatter", "configure_logging", "get_logger"]

