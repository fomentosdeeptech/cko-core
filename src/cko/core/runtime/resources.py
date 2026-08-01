"""In-memory registry for logical Runtime resources."""

from __future__ import annotations

import math
from types import MappingProxyType
from typing import Iterator, Mapping

from .errors import ResourceRegistryError


def _name(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ResourceRegistryError("resource name must be non-empty")
    return value.strip()


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ResourceRegistryError("resource numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen = {_name(key): _freeze(item) for key, item in value.items()}
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(item) for item in value)
    raise ResourceRegistryError(
        f"unsupported logical resource value: {type(value).__name__}"
    )


class ResourceRegistry:
    """Register serializable logical resources without acquiring external ones."""

    def __init__(self) -> None:
        self._resources: dict[str, object] = {}

    def register(self, name: str, value: object = None) -> None:
        """Register one unique logical resource."""
        normalized = _name(name)
        if normalized in self._resources:
            raise ResourceRegistryError(f"resource already registered: {normalized}")
        self._resources[normalized] = _freeze(value)

    def unregister(self, name: str) -> object:
        """Remove and return one registered logical resource."""
        normalized = _name(name)
        try:
            return self._resources.pop(normalized)
        except KeyError as error:
            raise ResourceRegistryError(
                f"resource is not registered: {normalized}"
            ) from error

    def get(self, name: str) -> object:
        """Return one registered logical resource."""
        normalized = _name(name)
        try:
            return self._resources[normalized]
        except KeyError as error:
            raise ResourceRegistryError(
                f"resource is not registered: {normalized}"
            ) from error

    def contains(self, name: str) -> bool:
        """Return whether a logical resource is registered."""
        return _name(name) in self._resources

    def snapshot(self) -> Mapping[str, object]:
        """Return an immutable, deterministic resource snapshot."""
        return MappingProxyType(dict(sorted(self._resources.items())))

    def clear(self) -> None:
        """Release all logical registrations without external side effects."""
        self._resources.clear()

    def __len__(self) -> int:
        return len(self._resources)

    def __iter__(self) -> Iterator[str]:
        return iter(sorted(self._resources))


__all__ = ["ResourceRegistry"]
