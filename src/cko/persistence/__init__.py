"""Núcleo persistente oficial introduzido na SPR-005A."""
from .database import Database, DatabaseError
from .migrations import MigrationManager

__all__ = ["Database", "DatabaseError", "MigrationManager"]
