"""Fluent builder for validated canonical inventories."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Self

from cko.core.identity import CanonicalId
from cko.core.models import Asset

from .engine import Inventory
from .errors import DuplicateAssetError


class InventoryBuilder:
    """Collect construction inputs before creating a valid inventory."""

    def __init__(self) -> None:
        self._inventory_id: CanonicalId | None = None
        self._name: str | None = None
        self._assets: dict[CanonicalId, Asset] = {}

    def identified_by(self, inventory_id: CanonicalId) -> Self:
        """Set the canonical inventory identifier."""
        self._inventory_id = inventory_id
        return self

    def named(self, name: str) -> Self:
        """Set the inventory display name."""
        self._name = name
        return self

    def add(self, asset: Asset) -> Self:
        """Add one canonical asset, rejecting duplicate identifiers."""
        if not isinstance(asset, Asset):
            raise TypeError("asset must be an Asset")
        if asset.id in self._assets:
            raise DuplicateAssetError(asset.id)
        self._assets[asset.id] = asset
        return self

    def extend(self, assets: Iterable[Asset]) -> Self:
        """Add canonical assets in iteration order."""
        for asset in assets:
            self.add(asset)
        return self

    def build(self) -> Inventory:
        """Build and validate the configured inventory."""
        if self._inventory_id is None:
            raise ValueError("inventory id was not configured")
        if self._name is None:
            raise ValueError("inventory name was not configured")
        return Inventory(self._inventory_id, self._name, self._assets.values())


__all__ = ["InventoryBuilder"]
