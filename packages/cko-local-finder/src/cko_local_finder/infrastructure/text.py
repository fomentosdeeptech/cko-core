"""Minimal deterministic text normalization."""

from __future__ import annotations

import unicodedata


class TextLimitError(ValueError):
    def __init__(self, observed: int, maximum: int) -> None:
        super().__init__(f"text character limit exceeded: {observed} > {maximum}")
        self.observed = observed
        self.maximum = maximum


def normalize_text(value: str, *, max_characters: int) -> str:
    if value.startswith("\ufeff"):
        value = value[1:]
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = unicodedata.normalize("NFC", value)
    if len(value) > max_characters:
        raise TextLimitError(len(value), max_characters)
    return value
