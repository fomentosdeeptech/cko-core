"""In-memory canonical inventory aggregate with no infrastructure access."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import json
from typing import Self

from cko.core.identity import CanonicalId
from cko.core.logging import get_logger
from cko.core.models import Asset, AssetLifecycle, AssetStatus, asset_from_dict

from .errors import AssetNotFoundError, DuplicateAssetError
from .models import (
    InventoryCollection,
    InventoryFilter,
    InventoryItem,
    InventoryQuery,
    InventoryResult,
    InventorySnapshot,
    InventoryStatistics,
    InventorySummary,
)
from .validator import InventoryValidator


_INVENTORY_SCHEMA_VERSION = "1.0"
_LOGGER = get_logger("core.inventory")


class Inventory:
    """Mutable aggregate that owns canonical assets and a logical revision."""

    def __init__(
        self,
        inventory_id: CanonicalId,
        name: str,
        assets: Iterable[Asset] = (),
        *,
        validator: InventoryValidator | None = None,
    ) -> None:
        if not isinstance(inventory_id, CanonicalId):
            raise TypeError("inventory_id must be CanonicalId")
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("name cannot be empty")
        self._id = inventory_id
        self._name = normalized_name
        self._items: dict[CanonicalId, InventoryItem] = {}
        self._revision = 0
        self._validator = validator or InventoryValidator()
        for asset in assets:
            self.register(asset)
        self._validator.ensure_valid(self._items)

    @property
    def id(self) -> CanonicalId:
        """Return the canonical inventory identifier."""
        return self._id

    @property
    def name(self) -> str:
        """Return the inventory display name."""
        return self._name

    @property
    def revision(self) -> int:
        """Return the logical revision incremented by each mutation."""
        return self._revision

    def __len__(self) -> int:
        return len(self._items)

    def register(self, asset: Asset, *, replace: bool = False) -> InventoryItem:
        """Register an asset, optionally replacing the same canonical id."""
        if not isinstance(asset, Asset):
            raise TypeError("asset must be an Asset")
        if asset.id in self._items and not replace:
            raise DuplicateAssetError(asset.id)
        item = InventoryItem(asset)
        candidate = dict(self._items)
        candidate[asset.id] = item
        self._validator.ensure_valid(candidate)
        self._items = candidate
        self._revision += 1
        _LOGGER.info(
            "asset registered",
            extra={
                "event": "inventory.asset.registered",
                "context": {
                    "inventory_id": str(self.id),
                    "asset_id": str(asset.id),
                    "revision": self.revision,
                },
            },
        )
        return item

    def remove(self, asset_id: CanonicalId) -> Asset:
        """Remove and return an asset by canonical identifier."""
        item = self._items.pop(asset_id, None)
        if item is None:
            raise AssetNotFoundError(asset_id)
        self._revision += 1
        _LOGGER.info(
            "asset removed",
            extra={
                "event": "inventory.asset.removed",
                "context": {
                    "inventory_id": str(self.id),
                    "asset_id": str(asset_id),
                    "revision": self.revision,
                },
            },
        )
        return item.asset

    def find(self, asset_id: CanonicalId) -> Asset | None:
        """Locate an asset by canonical identifier without raising."""
        item = self._items.get(asset_id)
        return None if item is None else item.asset

    def require(self, asset_id: CanonicalId) -> Asset:
        """Locate an asset or raise a stable domain error."""
        asset = self.find(asset_id)
        if asset is None:
            raise AssetNotFoundError(asset_id)
        return asset

    def find_by_type(self, asset_type: type[Asset] | str) -> InventoryCollection:
        """Locate assets by canonical class or canonical kind string."""
        if isinstance(asset_type, str):
            return self._filtered(InventoryFilter(types=(asset_type,)))
        return InventoryCollection(
            tuple(
                item
                for item in self._ordered_items()
                if isinstance(item.asset, asset_type)
            )
        )

    def find_by_classification(
        self,
        scheme: str,
        value: str,
    ) -> InventoryCollection:
        """Locate assets with an exact canonical classification."""
        return self._filtered(
            InventoryFilter(classifications=((scheme, value),))
        )

    def find_by_status(self, status: AssetStatus) -> InventoryCollection:
        """Locate assets by canonical status."""
        return self._filtered(InventoryFilter(statuses=(status,)))

    def find_by_lifecycle(
        self,
        lifecycle: AssetLifecycle,
    ) -> InventoryCollection:
        """Locate assets by canonical lifecycle stage."""
        return self._filtered(InventoryFilter(lifecycles=(lifecycle,)))

    def query(self, query: InventoryQuery) -> InventoryResult:
        """Execute a deterministic in-memory query."""
        matched = [
            item for item in self._items.values() if query.filter.matches(item.asset)
        ]
        keys = {
            "id": lambda item: str(item.id),
            "name": lambda item: (item.asset.name.casefold(), str(item.id)),
            "type": lambda item: (item.asset.kind, str(item.id)),
        }
        matched.sort(key=keys[query.sort_by], reverse=query.descending)
        total = len(matched)
        stop = None if query.limit is None else query.offset + query.limit
        page = matched[query.offset:stop]
        return InventoryResult(
            InventoryCollection(tuple(page)),
            total,
            query.offset,
            query.limit,
        )

    def snapshot(self) -> InventorySnapshot:
        """Produce an immutable view detached from future mutations."""
        return InventorySnapshot(
            inventory_id=self.id,
            name=self.name,
            revision=self.revision,
            collection=InventoryCollection(self._ordered_items()),
        )

    def statistics(self) -> InventoryStatistics:
        """Calculate statistics from current canonical assets."""
        return InventoryStatistics.from_collection(self.snapshot().collection)

    def summary(self) -> InventorySummary:
        """Produce a concise summary of the current revision."""
        return InventorySummary(
            inventory_id=self.id,
            name=self.name,
            revision=self.revision,
            statistics=self.statistics(),
        )

    def validate(self) -> tuple[str, ...]:
        """Return all current internal consistency violations."""
        return self._validator.validate(self._items)

    def ensure_valid(self) -> None:
        """Raise when internal consistency is violated."""
        self._validator.ensure_valid(self._items)

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete inventory without persistence side effects."""
        return {
            "schema_version": _INVENTORY_SCHEMA_VERSION,
            "inventory_id": str(self.id),
            "name": self.name,
            "revision": self.revision,
            "assets": [item.asset.to_dict() for item in self._ordered_items()],
        }

    def to_json(self) -> str:
        """Serialize the inventory as deterministic UTF-8 JSON."""
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore a canonical inventory from serialized primitives."""
        if payload.get("schema_version") != _INVENTORY_SCHEMA_VERSION:
            raise ValueError("unsupported inventory schema_version")
        raw_assets = payload.get("assets")
        if not isinstance(raw_assets, list):
            raise ValueError("assets must be a list")
        assets: list[Asset] = []
        for raw_asset in raw_assets:
            if not isinstance(raw_asset, Mapping):
                raise ValueError("every asset must be an object")
            assets.append(asset_from_dict(raw_asset))
        inventory = cls(
            CanonicalId.parse(str(payload["inventory_id"])),
            str(payload["name"]),
            assets,
        )
        revision = int(payload["revision"])
        if revision < len(assets):
            raise ValueError("revision cannot be lower than asset count")
        inventory._revision = revision
        return inventory

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Restore a canonical inventory from a JSON object."""
        decoded = json.loads(payload)
        if not isinstance(decoded, dict):
            raise ValueError("inventory JSON must contain an object")
        return cls.from_dict(decoded)

    def _ordered_items(self) -> tuple[InventoryItem, ...]:
        return tuple(
            sorted(self._items.values(), key=lambda item: str(item.id))
        )

    def _filtered(self, inventory_filter: InventoryFilter) -> InventoryCollection:
        return InventoryCollection(
            tuple(
                item
                for item in self._ordered_items()
                if inventory_filter.matches(item.asset)
            )
        )


__all__ = ["Inventory"]
