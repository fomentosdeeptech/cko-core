"""Contratos internos estáveis do CKO."""

from .repositories import DocumentRepository
from .scanner import FileScanner, ScannedFile

__all__ = ["DocumentRepository", "FileScanner", "ScannedFile"]
