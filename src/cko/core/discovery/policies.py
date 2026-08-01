"""Neutral policy validation for the Discovery boundary."""

from __future__ import annotations

from collections.abc import Iterable

from .errors import UnsupportedDiscoveryCapabilityError
from .models import DiscoveryCapability, DiscoveryPolicy


def ensure_supported_capabilities(
    required: Iterable[DiscoveryCapability],
    available: Iterable[DiscoveryCapability],
) -> None:
    """Reject capabilities required by a request but absent from a source."""
    missing = frozenset(required) - frozenset(available)
    if missing:
        values = ", ".join(sorted(capability.value for capability in missing))
        raise UnsupportedDiscoveryCapabilityError(
            f"source does not support required capabilities: {values}"
        )


def validate_policy(policy: DiscoveryPolicy) -> None:
    """Validate cross-field neutral limits not enforced by construction."""
    if (
        policy.max_items is not None
        and policy.page_size is not None
        and policy.page_size > policy.max_items
    ):
        raise ValueError("page_size cannot exceed max_items")


__all__ = ["ensure_supported_capabilities", "validate_policy"]
