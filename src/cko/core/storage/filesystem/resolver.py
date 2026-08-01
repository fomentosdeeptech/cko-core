"""Safe translation from logical StorageLocation values to filesystem paths."""

from __future__ import annotations

from pathlib import Path, PurePath

from cko.core.storage import StorageException, StorageLocation


class FilesystemLocationResolver:
    """Resolve logical locations below one configured filesystem root."""

    def __init__(self, root: str | Path) -> None:
        if not isinstance(root, (str, Path)) or not str(root).strip():
            raise StorageException("root must be a filesystem path")
        self._root = Path(root).expanduser().resolve(strict=False)

    @property
    def root(self) -> Path:
        """Return the normalized physical root of this resolver."""
        return self._root

    def resolve(self, location: StorageLocation) -> Path:
        """Resolve a public logical location within the configured root."""
        if not isinstance(location, StorageLocation):
            raise StorageException("location must be StorageLocation")
        self._validate_part(location.namespace, "namespace")
        self._validate_part(location.key, "key")
        candidate = (self._root / location.namespace / location.key).resolve(
            strict=False
        )
        if not candidate.is_relative_to(self._root):
            raise StorageException(
                "storage location resolves outside the filesystem root",
                code="invalid_location",
            )
        return candidate

    def logical(self, path: str | Path) -> StorageLocation:
        """Translate a physical descendant back to a StorageLocation."""
        if not isinstance(path, (str, Path)) or not str(path).strip():
            raise StorageException("path must be a filesystem path")
        resolved = Path(path).resolve(strict=False)
        if not resolved.is_relative_to(self._root):
            raise StorageException(
                "filesystem path is outside the configured root",
                code="invalid_location",
            )
        relative = resolved.relative_to(self._root)
        if not relative.parts:
            raise StorageException("filesystem path has no logical namespace")
        key = (
            "."
            if len(relative.parts) == 1
            else PurePath(*relative.parts[1:]).as_posix()
        )
        return StorageLocation(
            namespace=relative.parts[0],
            key=key,
        )

    @staticmethod
    def _validate_part(value: str, name: str) -> None:
        path = PurePath(value)
        if path.is_absolute() or ".." in path.parts:
            raise StorageException(
                f"{name} must be a relative logical path",
                code="invalid_location",
            )


__all__ = ["FilesystemLocationResolver"]
