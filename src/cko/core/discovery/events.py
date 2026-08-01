"""Stable event names and canonical event construction for Discovery."""

from __future__ import annotations

from datetime import datetime
from typing import Mapping

from cko.core.identity import CanonicalId, Origin
from cko.core.models import CanonicalEvent

from .models import DiscoverySourceId


DISCOVERY_STARTED = "discovery.started"
DISCOVERY_ITEM_OBSERVED = "discovery.item.observed"
DISCOVERY_ITEM_REJECTED = "discovery.item.rejected"
DISCOVERY_BATCH_COMPLETED = "discovery.batch.completed"
DISCOVERY_COMPLETED = "discovery.completed"
DISCOVERY_FAILED = "discovery.failed"
DISCOVERY_CANCELLED = "discovery.cancelled"

DISCOVERY_EVENT_NAMES = frozenset(
    {
        DISCOVERY_STARTED,
        DISCOVERY_ITEM_OBSERVED,
        DISCOVERY_ITEM_REJECTED,
        DISCOVERY_BATCH_COMPLETED,
        DISCOVERY_COMPLETED,
        DISCOVERY_FAILED,
        DISCOVERY_CANCELLED,
    }
)


def create_discovery_event(
    name: str,
    occurred_at: datetime,
    source_id: DiscoverySourceId,
    attributes: Mapping[str, object] | None = None,
) -> CanonicalEvent:
    """Build a canonical event while keeping transport outside the core."""
    if name not in DISCOVERY_EVENT_NAMES:
        raise ValueError(f"unsupported discovery event name: {name}")
    return CanonicalEvent(
        id=CanonicalId.new(),
        name=name,
        occurred_at=occurred_at,
        origin=Origin(
            system="cko.core.discovery",
            captured_at=occurred_at,
            reference=str(source_id),
        ),
        attributes={} if attributes is None else attributes,
    )


__all__ = [
    "DISCOVERY_BATCH_COMPLETED", "DISCOVERY_CANCELLED", "DISCOVERY_COMPLETED",
    "DISCOVERY_EVENT_NAMES", "DISCOVERY_FAILED", "DISCOVERY_ITEM_OBSERVED",
    "DISCOVERY_ITEM_REJECTED", "DISCOVERY_STARTED", "create_discovery_event",
]
