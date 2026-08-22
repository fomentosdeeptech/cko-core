"""Application coordination for deterministic internal reports."""

from cko_local_finder.application.ports import ProvenancePort
from cko_local_finder.domain.models import DuplicateReport, FailureReport, IngestionReport


def build_ingestion_report(root: str, observed_at: str, repository: ProvenancePort) -> IngestionReport:
    if not root or not observed_at: raise ValueError("explicit root and observed_at are required")
    repository.apply_provenance_migrations()
    return repository.ingestion_report(root, observed_at)


def build_failure_report(root: str | None, observed_at: str, repository: ProvenancePort) -> FailureReport:
    if not observed_at: raise ValueError("explicit observed_at is required")
    repository.apply_provenance_migrations()
    return repository.failure_report(root, observed_at)


def build_duplicate_report(root: str | None, observed_at: str, repository: ProvenancePort) -> DuplicateReport:
    if not observed_at: raise ValueError("explicit observed_at is required")
    repository.apply_provenance_migrations()
    return repository.duplicate_report(root, observed_at)
