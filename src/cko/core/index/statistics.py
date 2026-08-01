"""Deterministic in-memory index statistics."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Callable

from .models import CanonicalIndex, IndexStatistics


class DefaultIndexStatisticsProvider:
    def __init__(self, clock: Callable[[],datetime] | None=None) -> None:
        self._clock=clock or (lambda: datetime.now(UTC))

    def calculate(self, index: CanonicalIndex) -> IndexStatistics:
        refs=[ref for entry in index.entries for ref in entry.references]
        unique={ref.sort_token for ref in refs}
        counts=[len(entry.references) for entry in index.entries]
        by_type=Counter(ref.entity_type.value for ref in refs)
        by_namespace=Counter(ref.namespace for ref in refs)
        return IndexStatistics(
            total_keys=len(index.entries), total_entries=len(index.entries),
            total_references=len(refs), total_unique_references=len(unique),
            average_references_per_key=(len(refs)/len(index.entries) if index.entries else 0.0),
            largest_cardinality=max(counts,default=0), smallest_cardinality=min(counts,default=0),
            empty_key_count=sum(entry.key.value in (None,"") for entry in index.entries),
            logical_collision_count=sum(max(0,value-1) for value in counts),
            by_entity_type=dict(sorted(by_type.items())), by_namespace=dict(sorted(by_namespace.items())),
            version=index.version.version, calculated_at=self._clock())


IndexStatisticsProvider=DefaultIndexStatisticsProvider
__all__=["DefaultIndexStatisticsProvider","IndexStatisticsProvider"]
