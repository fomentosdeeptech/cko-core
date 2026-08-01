"""Immutable value objects used by the canonical inventory engine."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
import json
from types import MappingProxyType
from typing import Self

from cko.core.identity import CanonicalId
from cko.core.models import (
    Asset,
    AssetLifecycle,
    AssetStatus,
    asset_from_dict,
)


_SNAPSHOT_SCHEMA_VERSION = "1.0"


def _frozen_counts(values: Mapping[str, int]) -> Mapping[str, int]:
    """Return an ordered, read-only copy of a count mapping."""
    return MappingProxyType(dict(sorted(values.items())))


@dataclass(frozen=True, slots=True)
class InventoryItem:
    """An asset registered in an inventory without infrastructure metadata."""

    asset: Asset

    def __post_init__(self) -> None:
        if not isinstance(self.asset, Asset):
            raise TypeError("asset must be an Asset")

    @property
    def id(self) -> CanonicalId:
        """Return the canonical identifier of the wrapped asset."""
        return self.asset.id

    def to_dict(self) -> dict[str, object]:
        """Serialize the item using the canonical asset envelope."""
        return {"asset": self.asset.to_dict()}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore an item from its canonical representation."""
        asset_payload = payload.get("asset")
        if not isinstance(asset_payload, Mapping):
            raise ValueError("asset must be an object")
        return cls(asset_from_dict(asset_payload))


@dataclass(frozen=True, slots=True)
class InventoryCollection:
    """Immutable, ordered collection of unique inventory items."""

    items: tuple[InventoryItem, ...] = ()

    def __post_init__(self) -> None:
        normalized = tuple(self.items)
        if any(not isinstance(item, InventoryItem) for item in normalized):
            raise TypeError("items must contain only InventoryItem values")
        identifiers = tuple(item.id for item in normalized)
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("inventory collection contains duplicate asset ids")
        object.__setattr__(self, "items", normalized)

    def __iter__(self) -> Iterator[InventoryItem]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def get(self, asset_id: CanonicalId) -> InventoryItem | None:
        """Find an item by canonical identifier."""
        return next((item for item in self.items if item.id == asset_id), None)

    def to_list(self) -> list[dict[str, object]]:
        """Serialize all items while preserving their order."""
        return [item.to_dict() for item in self.items]

    @classmethod
    def from_list(cls, payload: object) -> Self:
        """Restore a collection from a list of item objects."""
        if not isinstance(payload, list):
            raise ValueError("items must be a list")
        if any(not isinstance(item, Mapping) for item in payload):
            raise ValueError("every item must be an object")
        return cls(tuple(InventoryItem.from_dict(item) for item in payload))


@dataclass(frozen=True, slots=True)
class InventorySnapshot:
    """Immutable point-in-time logical view of an inventory revision."""

    inventory_id: CanonicalId
    name: str
    revision: int
    collection: InventoryCollection

    def __post_init__(self) -> None:
        if not isinstance(self.inventory_id, CanonicalId):
            raise TypeError("inventory_id must be CanonicalId")
        if not self.name.strip():
            raise ValueError("name cannot be empty")
        if self.revision < 0:
            raise ValueError("revision cannot be negative")

    def to_dict(self) -> dict[str, object]:
        """Serialize the snapshot as a versioned canonical envelope."""
        return {
            "schema_version": _SNAPSHOT_SCHEMA_VERSION,
            "inventory_id": str(self.inventory_id),
            "name": self.name,
            "revision": self.revision,
            "items": self.collection.to_list(),
        }

    def to_json(self) -> str:
        """Serialize the snapshot as deterministic UTF-8 JSON."""
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Restore and validate a serialized snapshot."""
        if payload.get("schema_version") != _SNAPSHOT_SCHEMA_VERSION:
            raise ValueError("unsupported inventory snapshot schema_version")
        return cls(
            inventory_id=CanonicalId.parse(str(payload["inventory_id"])),
            name=str(payload["name"]),
            revision=int(payload["revision"]),
            collection=InventoryCollection.from_list(payload.get("items")),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Restore a snapshot from a JSON object."""
        decoded = json.loads(payload)
        if not isinstance(decoded, dict):
            raise ValueError("inventory snapshot JSON must contain an object")
        return cls.from_dict(decoded)


@dataclass(frozen=True, slots=True)
class InventoryStatistics:
    """Immutable aggregations calculated from canonical asset properties."""

    total: int
    by_type: Mapping[str, int] = field(default_factory=dict)
    by_status: Mapping[str, int] = field(default_factory=dict)
    by_lifecycle: Mapping[str, int] = field(default_factory=dict)
    by_classification: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.total < 0:
            raise ValueError("total cannot be negative")
        for name in (
            "by_type",
            "by_status",
            "by_lifecycle",
            "by_classification",
        ):
            values = getattr(self, name)
            if any(count < 0 for count in values.values()):
                raise ValueError(f"{name} cannot contain negative counts")
            object.__setattr__(self, name, _frozen_counts(values))

    @classmethod
    def from_collection(cls, collection: InventoryCollection) -> Self:
        """Calculate statistics for a canonical collection."""
        assets = tuple(item.asset for item in collection)
        classifications = Counter(
            f"{classification.scheme}:{classification.value}"
            for asset in assets
            for classification in asset.classifications
        )
        return cls(
            total=len(assets),
            by_type=Counter(asset.kind for asset in assets),
            by_status=Counter(asset.status.value for asset in assets),
            by_lifecycle=Counter(asset.lifecycle.value for asset in assets),
            by_classification=classifications,
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize statistics into mutable JSON-compatible mappings."""
        return {
            "total": self.total,
            "by_type": dict(self.by_type),
            "by_status": dict(self.by_status),
            "by_lifecycle": dict(self.by_lifecycle),
            "by_classification": dict(self.by_classification),
        }


@dataclass(frozen=True, slots=True)
class InventorySummary:
    """Concise immutable description of an inventory revision."""

    inventory_id: CanonicalId
    name: str
    revision: int
    statistics: InventoryStatistics

    def to_dict(self) -> dict[str, object]:
        """Serialize the summary to JSON-compatible primitives."""
        return {
            "inventory_id": str(self.inventory_id),
            "name": self.name,
            "revision": self.revision,
            "statistics": self.statistics.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class InventoryFilter:
    """Composable exact-match filter over canonical asset fields."""

    ids: tuple[CanonicalId, ...] = ()
    types: tuple[str, ...] = ()
    classifications: tuple[tuple[str, str], ...] = ()
    statuses: tuple[AssetStatus, ...] = ()
    lifecycles: tuple[AssetLifecycle, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "ids", tuple(self.ids))
        object.__setattr__(self, "types", tuple(self.types))
        object.__setattr__(
            self,
            "classifications",
            tuple((scheme, value) for scheme, value in self.classifications),
        )
        object.__setattr__(
            self,
            "statuses",
            tuple(AssetStatus(status) for status in self.statuses),
        )
        object.__setattr__(
            self,
            "lifecycles",
            tuple(AssetLifecycle(lifecycle) for lifecycle in self.lifecycles),
        )
        if any(not kind.strip() for kind in self.types):
            raise ValueError("types cannot contain empty values")
        if any(
            not scheme.strip() or not value.strip()
            for scheme, value in self.classifications
        ):
            raise ValueError("classifications cannot contain empty values")

    def matches(self, asset: Asset) -> bool:
        """Return whether an asset satisfies every populated criterion."""
        if self.ids and asset.id not in self.ids:
            return False
        if self.types and asset.kind not in self.types:
            return False
        if self.statuses and asset.status not in self.statuses:
            return False
        if self.lifecycles and asset.lifecycle not in self.lifecycles:
            return False
        available = {
            (classification.scheme, classification.value)
            for classification in asset.classifications
        }
        return not self.classifications or all(
            expected in available for expected in self.classifications
        )


@dataclass(frozen=True, slots=True)
class InventoryQuery:
    """Query definition with deterministic sorting and pagination."""

    filter: InventoryFilter = field(default_factory=InventoryFilter)
    offset: int = 0
    limit: int | None = None
    sort_by: str = "id"
    descending: bool = False

    def __post_init__(self) -> None:
        if self.offset < 0:
            raise ValueError("offset cannot be negative")
        if self.limit is not None and self.limit <= 0:
            raise ValueError("limit must be greater than zero")
        if self.sort_by not in {"id", "name", "type"}:
            raise ValueError("sort_by must be id, name, or type")


@dataclass(frozen=True, slots=True)
class InventoryResult:
    """Immutable paginated result produced by an inventory query."""

    collection: InventoryCollection
    total: int
    offset: int
    limit: int | None

    def __post_init__(self) -> None:
        if self.total < 0 or self.offset < 0:
            raise ValueError("total and offset cannot be negative")
        if self.limit is not None and self.limit <= 0:
            raise ValueError("limit must be greater than zero")

    def to_dict(self) -> dict[str, object]:
        """Serialize the query result."""
        return {
            "items": self.collection.to_list(),
            "total": self.total,
            "offset": self.offset,
            "limit": self.limit,
        }


__all__ = [
    "InventoryCollection",
    "InventoryFilter",
    "InventoryItem",
    "InventoryQuery",
    "InventoryResult",
    "InventorySnapshot",
    "InventoryStatistics",
    "InventorySummary",
]
