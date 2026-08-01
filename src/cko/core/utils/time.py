"""Operações de tempo explícitas e seguras para modelos canônicos."""

from datetime import UTC, datetime


def ensure_aware(value: datetime) -> datetime:
    """Valida presença de fuso e normaliza um instante para UTC."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime deve possuir fuso horário")
    return value.astimezone(UTC)


def utc_now() -> datetime:
    """Retorna o instante atual em UTC com fuso explícito."""
    return datetime.now(UTC)

