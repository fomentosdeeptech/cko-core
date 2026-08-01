"""Domain errors exposed by the canonical inventory engine."""

from __future__ import annotations

from cko.core.exceptions import ContractError, ModelValidationError
from cko.core.identity import CanonicalId


class InventoryError(ContractError):
    """Base error for inventory operations."""


class DuplicateAssetError(InventoryError):
    """Raised when an inventory already contains an asset identifier."""

    def __init__(self, asset_id: CanonicalId) -> None:
        super().__init__(f"asset already registered: {asset_id}")
        self.asset_id = asset_id


class AssetNotFoundError(InventoryError, KeyError):
    """Raised when an asset identifier is absent from an inventory."""

    def __init__(self, asset_id: CanonicalId) -> None:
        super().__init__(f"asset not found: {asset_id}")
        self.asset_id = asset_id


class InventoryValidationError(ModelValidationError):
    """Raised when an inventory violates one or more consistency rules."""

    def __init__(self, violations: tuple[str, ...]) -> None:
        if not violations:
            raise ValueError("violations cannot be empty")
        super().__init__("; ".join(violations))
        self.violations = violations


__all__ = [
    "AssetNotFoundError",
    "DuplicateAssetError",
    "InventoryError",
    "InventoryValidationError",
]
