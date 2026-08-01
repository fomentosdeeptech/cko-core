"""Application facade for the canonical inventory aggregate."""

from __future__ import annotations

from cko.core.identity import CanonicalId
from cko.core.models import Asset

from .engine import Inventory
from .models import (
    InventoryItem,
    InventoryQuery,
    InventoryResult,
    InventorySnapshot,
    InventoryStatistics,
    InventorySummary,
)


class InventoryService:
    """Expose inventory use cases without persistence or adapter knowledge."""

    def __init__(self, inventory: Inventory) -> None:
        if not isinstance(inventory, Inventory):
            raise TypeError("inventory must be an Inventory")
        self._inventory = inventory

    @property
    def inventory(self) -> Inventory:
        """Return the managed inventory aggregate."""
        return self._inventory

    def register(self, asset: Asset, *, replace: bool = False) -> InventoryItem:
        """Register a canonical asset."""
        return self.inventory.register(asset, replace=replace)

    def remove(self, asset_id: CanonicalId) -> Asset:
        """Remove a canonical asset."""
        return self.inventory.remove(asset_id)

    def query(self, query: InventoryQuery) -> InventoryResult:
        """Execute a canonical query."""
        return self.inventory.query(query)

    def snapshot(self) -> InventorySnapshot:
        """Create an immutable inventory snapshot."""
        return self.inventory.snapshot()

    def statistics(self) -> InventoryStatistics:
        """Calculate current inventory statistics."""
        return self.inventory.statistics()

    def summary(self) -> InventorySummary:
        """Create the current inventory summary."""
        return self.inventory.summary()

    def validate(self) -> tuple[str, ...]:
        """Return current consistency violations."""
        return self.inventory.validate()


__all__ = ["InventoryService"]
