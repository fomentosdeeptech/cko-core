"""Modelos arquiteturais do CKO."""

from .document import DocumentRecord, FileLocationRecord
from .job import JobRecord, JobStatus

__all__ = [
    "DocumentRecord",
    "FileLocationRecord",
    "JobRecord",
    "JobStatus",
]
