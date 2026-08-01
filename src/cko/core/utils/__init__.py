"""Utilitários puros e reutilizáveis do núcleo canônico."""

from .text import require_non_empty
from .time import ensure_aware, utc_now

__all__ = ["ensure_aware", "require_non_empty", "utc_now"]

