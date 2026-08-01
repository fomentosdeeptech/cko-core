"""Controlled mapping from observations to canonical Assets."""

from __future__ import annotations

from cko.core.models import Asset

from .errors import DiscoveryMappingError
from .models import DiscoveredItem


class DefaultDiscoveryAssetMapper:
    """Create a base Asset only when canonical identity is already available."""

    def map_item(self, item: DiscoveredItem) -> Asset:
        """Map an item without persistence or institutional classification."""
        if item.canonical_id is None:
            raise DiscoveryMappingError(
                "a canonical_id is required before mapping an observation"
            )
        name = item.attributes.get("name", item.external_reference)
        if not isinstance(name, str) or not name.strip():
            raise DiscoveryMappingError("item name must be a non-empty string")
        try:
            return Asset(
                id=item.canonical_id,
                name=name,
                metadata=item.metadata,
                created_at=item.metadata.created_at,
                updated_at=item.observed_at,
                attributes={
                    "discovery_source_id": str(item.source_id),
                    "external_reference": item.external_reference,
                    "correlation_id": item.correlation_id,
                    "observation_method": item.observation_method,
                },
            )
        except (TypeError, ValueError) as error:
            raise DiscoveryMappingError(
                "observation cannot be mapped to Asset"
            ) from error


__all__ = ["DefaultDiscoveryAssetMapper"]
