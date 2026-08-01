"""Abstract checkpoint contract for Discovery execution continuity."""

from __future__ import annotations

from typing import Mapping, Protocol, runtime_checkable

from cko.core.identity import CanonicalId


@runtime_checkable
class DiscoveryCheckpoint(Protocol):
    """Read-only checkpoint value supplied by an external implementation."""

    @property
    def id(self) -> CanonicalId:
        """Return the checkpoint canonical identity."""
        raise RuntimeError("abstract checkpoint contract has no identity")

    @property
    def session_id(self) -> CanonicalId:
        """Return the session identity that owns the checkpoint."""
        raise RuntimeError("abstract checkpoint contract has no session")

    @property
    def sequence(self) -> int:
        """Return the monotonically increasing logical sequence."""
        raise RuntimeError("abstract checkpoint contract has no sequence")

    @property
    def context(self) -> Mapping[str, object]:
        """Return provider-neutral continuation context."""
        raise RuntimeError("abstract checkpoint contract has no context")


__all__ = ["DiscoveryCheckpoint"]
