"""Validações textuais pequenas e livres de regra de negócio."""


def require_non_empty(value: str, field_name: str) -> str:
    """Remove espaços externos e rejeita texto vazio."""
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} não pode ser vazio")
    return normalized

