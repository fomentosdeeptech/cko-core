"""Pure duplicate grouping by physical SHA-256 identity."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from cko_local_finder.domain.models import DiscoveredFile, DuplicateGroup


def group_duplicates(files: Iterable[DiscoveredFile]) -> tuple[DuplicateGroup, ...]:
    """Group all locations sharing a digest without choosing a primary copy."""
    grouped: dict[str, list[DiscoveredFile]] = defaultdict(list)
    for item in files:
        grouped[item.sha256].append(item)
    results = []
    for digest, members in grouped.items():
        paths = tuple(sorted({item.relative_path for item in members}, key=lambda value: (value.casefold(), value)))
        if len(paths) < 2:
            continue
        sizes = {item.size_bytes for item in members}
        if len(sizes) != 1:
            raise ValueError("files with one SHA-256 must have a consistent size")
        results.append(DuplicateGroup(digest, sizes.pop(), paths))
    return tuple(sorted(results, key=lambda item: item.sha256))
