"""Modelo mínimo de jobs para pipelines futuros."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class JobStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRY = "RETRY"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class JobRecord:
    job_id: UUID
    job_type: str
    status: JobStatus
    created_at: datetime
