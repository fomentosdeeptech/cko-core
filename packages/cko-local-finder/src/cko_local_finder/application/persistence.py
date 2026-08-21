"""Application service for one transactional discovery persistence unit."""

from __future__ import annotations

from datetime import datetime, timezone

from cko_local_finder.application.ports import DocumentRepositoryPort
from cko_local_finder.domain.models import DiscoveryReport, PersistenceSummary


def persist_discovery_report(
    report: DiscoveryReport,
    repository: DocumentRepositoryPort,
    *,
    observed_at: str | None = None,
) -> PersistenceSummary:
    """Persist one immutable discovery report without rediscovery or hashing."""
    timestamp = observed_at or datetime.now(timezone.utc).isoformat()
    repository.apply_migrations()
    with repository.transaction():
        return repository.persist_report(report, timestamp)
