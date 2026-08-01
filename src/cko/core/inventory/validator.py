"""Internal consistency validation for canonical inventories."""

from __future__ import annotations

from collections.abc import Mapping

from cko.core.identity import CanonicalId

from .errors import InventoryValidationError
from .models import InventoryItem


class InventoryValidator:
    """Validate identifiers and nested canonical references without I/O."""

    def validate(
        self,
        items: Mapping[CanonicalId, InventoryItem],
    ) -> tuple[str, ...]:
        """Return every detected violation in stable order."""
        violations: list[str] = []
        nested_ids: set[CanonicalId] = set()
        for key, item in sorted(items.items(), key=lambda entry: str(entry[0])):
            if key != item.id:
                violations.append(f"item key differs from asset id: {key}")
            for classification in item.asset.classifications:
                if classification.asset_id != item.id:
                    violations.append(
                        f"classification {classification.id} references another asset"
                    )
                if classification.id in nested_ids:
                    violations.append(
                        f"duplicate nested canonical id: {classification.id}"
                    )
                nested_ids.add(classification.id)
            for fingerprint in item.asset.fingerprints:
                if fingerprint.asset_id != item.id:
                    violations.append(
                        f"fingerprint {fingerprint.id} references another asset"
                    )
                if fingerprint.id in nested_ids:
                    violations.append(
                        f"duplicate nested canonical id: {fingerprint.id}"
                    )
                nested_ids.add(fingerprint.id)
            for asset_hash in item.asset.hashes:
                if asset_hash.asset_id != item.id:
                    violations.append(
                        f"hash {asset_hash.id} references another asset"
                    )
                if asset_hash.id in nested_ids:
                    violations.append(f"duplicate nested canonical id: {asset_hash.id}")
                nested_ids.add(asset_hash.id)
        return tuple(violations)

    def ensure_valid(self, items: Mapping[CanonicalId, InventoryItem]) -> None:
        """Raise a domain error when consistency validation fails."""
        violations = self.validate(items)
        if violations:
            raise InventoryValidationError(violations)


__all__ = ["InventoryValidator"]
