"""Concrete standard-library filesystem implementation of Storage."""

from __future__ import annotations

import base64
import binascii
import hashlib
import shutil
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping

from cko.core.logging import get_logger
from cko.core.storage import (
    Storage,
    StorageDescriptor,
    StorageException,
    StorageLocation,
    StorageObject,
    StorageOperation,
    StorageResult,
    StorageSession,
    StorageValidator,
)

from .descriptor import FilesystemDescriptor
from .resolver import FilesystemLocationResolver


class FilesystemStorage(Storage):
    """Persist logical storage objects below one configured filesystem root."""

    def __init__(
        self,
        root: str | Path,
        descriptor: StorageDescriptor | None = None,
        validator: StorageValidator | None = None,
    ) -> None:
        self._resolver = FilesystemLocationResolver(root)
        self._descriptor = descriptor or FilesystemDescriptor().storage
        self._validator = validator or StorageValidator()
        if not isinstance(self._validator, StorageValidator):
            raise StorageException("validator must be StorageValidator")
        self._validator.validate_descriptor(self._descriptor)
        self._resolver.root.mkdir(parents=True, exist_ok=True)
        if not self._resolver.root.is_dir():
            raise StorageException("filesystem root must be a directory")
        self._logger = get_logger("core.storage.filesystem")
        self._log("filesystem_open", root=str(self._resolver.root))

    @property
    def descriptor(self) -> StorageDescriptor:
        """Return the canonical public Storage descriptor."""
        return self._descriptor

    @property
    def resolver(self) -> FilesystemLocationResolver:
        """Return the logical location resolver used by this adapter."""
        return self._resolver

    def execute(self, session: StorageSession) -> StorageResult:
        """Execute the operation represented by a validated StorageSession."""
        self._validator.validate_session(session, self._descriptor)
        operation = session.context.operation
        filesystem_operation = session.context.parameters.get(
            "filesystem_operation", operation.value
        )
        dispatch: dict[str, Callable[[StorageSession], StorageResult]] = {
            "copy": self.copy,
            "create": self.create,
            "delete": self.delete,
            "exists": self.exists,
            "list": self.list,
            "metadata": self.metadata,
            "move": self.move,
            "read": self.read,
            "write": self.write,
        }
        if not isinstance(filesystem_operation, str):
            return self._failure(session, "filesystem_operation must be a string")
        handler = dispatch.get(filesystem_operation)
        if handler is None:
            return self._failure(
                session,
                f"unsupported filesystem operation: {filesystem_operation}",
            )
        mapped_operations = {
            "copy": StorageOperation.WRITE,
            "create": StorageOperation.WRITE,
            "move": StorageOperation.WRITE,
        }
        compatible = mapped_operations.get(filesystem_operation)
        if compatible is None:
            compatible = StorageOperation(filesystem_operation)
        if operation is not compatible:
            return self._failure(
                session,
                "filesystem operation is incompatible with StorageOperation",
            )
        return handler(session)

    def create(self, session: StorageSession) -> StorageResult:
        """Create one empty or initialized file, or one directory."""
        return self._run(session, "filesystem_write", self._create)

    def read(self, session: StorageSession) -> StorageResult:
        """Read one file and return its bytes as serializable Base64."""
        return self._run(session, "filesystem_read", self._read)

    def write(self, session: StorageSession) -> StorageResult:
        """Write serializable text or Base64 content to one file."""
        return self._run(session, "filesystem_write", self._write)

    def delete(self, session: StorageSession) -> StorageResult:
        """Delete one file or directory addressed by the session."""
        return self._run(session, "filesystem_delete", self._delete)

    def exists(self, session: StorageSession) -> StorageResult:
        """Report whether one logical location exists."""
        return self._run(session, None, self._exists)

    def list(self, session: StorageSession) -> StorageResult:
        """Enumerate descendants in deterministic lexical order."""
        return self._run(session, "filesystem_list", self._list)

    def copy(self, session: StorageSession) -> StorageResult:
        """Copy one file or directory to a target StorageLocation."""
        return self._run(session, "filesystem_copy", self._copy)

    def move(self, session: StorageSession) -> StorageResult:
        """Move one file or directory to a target StorageLocation."""
        return self._run(session, "filesystem_move", self._move)

    def metadata(self, session: StorageSession) -> StorageResult:
        """Return a canonical StorageObject for one logical location."""
        return self._run(session, None, self._metadata)

    def _run(
        self,
        session: StorageSession,
        event: str | None,
        operation: Callable[[StorageSession], StorageResult],
    ) -> StorageResult:
        try:
            self._validator.validate_session(session, self._descriptor)
            result = operation(session)
        except (StorageException, OSError, ValueError, TypeError) as error:
            result = self._failure(session, str(error))
        if event is not None:
            self._log(
                event,
                location=session.context.location.to_dict(),
                success=result.success,
            )
        return result

    def _create(self, session: StorageSession) -> StorageResult:
        path = self._resolver.resolve(session.context.location)
        kind = session.context.parameters.get("kind", "file")
        if kind == "directory":
            path.mkdir(parents=True, exist_ok=False)
        elif kind == "file":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self._content(session.context.parameters))
        else:
            raise StorageException("kind must be file or directory")
        return self._success(session, (self._object(path),))

    def _read(self, session: StorageSession) -> StorageResult:
        path = self._resolver.resolve(session.context.location)
        content = path.read_bytes()
        metadata: dict[str, object] = {
            "content_base64": base64.b64encode(content).decode("ascii"),
            "size": len(content),
        }
        if session.context.parameters.get("include_text", False):
            encoding = self._encoding(session.context.parameters)
            metadata["content"] = content.decode(encoding)
            metadata["encoding"] = encoding
        return self._success(session, (self._object(path),), metadata)

    def _write(self, session: StorageSession) -> StorageResult:
        path = self._resolver.resolve(session.context.location)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self._content(session.context.parameters))
        return self._success(session, (self._object(path),))

    def _delete(self, session: StorageSession) -> StorageResult:
        path = self._resolver.resolve(session.context.location)
        deleted = self._object(path)
        if path.is_dir():
            recursive = session.context.parameters.get("recursive", False)
            if not isinstance(recursive, bool):
                raise StorageException("recursive must be boolean")
            if recursive:
                shutil.rmtree(path)
            else:
                path.rmdir()
        else:
            path.unlink()
        return self._success(session, (deleted,))

    def _exists(self, session: StorageSession) -> StorageResult:
        path = self._resolver.resolve(session.context.location)
        objects = (self._object(path),) if path.exists() else ()
        return self._success(
            session,
            objects,
            {"exists": path.exists()},
        )

    def _list(self, session: StorageSession) -> StorageResult:
        path = self._resolver.resolve(session.context.location)
        if not path.is_dir():
            raise StorageException("list location must be a directory")
        recursive = session.context.parameters.get("recursive", False)
        if not isinstance(recursive, bool):
            raise StorageException("recursive must be boolean")
        entries = path.rglob("*") if recursive else path.iterdir()
        ordered = sorted(entries, key=lambda item: item.as_posix())
        objects = tuple(self._object(item) for item in ordered)
        return self._success(session, objects, {"count": len(objects)})

    def _copy(self, session: StorageSession) -> StorageResult:
        source = self._resolver.resolve(session.context.location)
        target = self._resolver.resolve(self._target(session))
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
        return self._success(session, (self._object(target),))

    def _move(self, session: StorageSession) -> StorageResult:
        source = self._resolver.resolve(session.context.location)
        target = self._resolver.resolve(self._target(session))
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise StorageException("move target already exists")
        shutil.move(str(source), str(target))
        return self._success(session, (self._object(target),))

    def _metadata(self, session: StorageSession) -> StorageResult:
        path = self._resolver.resolve(session.context.location)
        return self._success(session, (self._object(path),))

    def _object(self, path: Path) -> StorageObject:
        if not path.exists():
            raise FileNotFoundError(str(path))
        location = self._resolver.logical(path)
        stat = path.stat()
        is_directory = path.is_dir()
        digest = None if is_directory else self._digest(path)
        size = None if is_directory else stat.st_size
        return StorageObject(
            object_id=f"{location.namespace}:{location.key}",
            location=location,
            size=size,
            digest=digest,
            metadata={
                "is_directory": is_directory,
                "modified_at": datetime.fromtimestamp(
                    stat.st_mtime, timezone.utc
                ).isoformat(),
            },
        )

    @staticmethod
    def _digest(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(65536), b""):
                digest.update(block)
        return f"sha256:{digest.hexdigest()}"

    @staticmethod
    def _encoding(parameters: Mapping[str, object]) -> str:
        encoding = parameters.get("encoding", "utf-8")
        if not isinstance(encoding, str) or not encoding.strip():
            raise StorageException("encoding must be a non-empty string")
        return encoding.strip()

    @classmethod
    def _content(cls, parameters: Mapping[str, object]) -> bytes:
        content = parameters.get("content")
        encoded = parameters.get("content_base64")
        if content is not None and encoded is not None:
            raise StorageException(
                "content and content_base64 are mutually exclusive"
            )
        if encoded is not None:
            if not isinstance(encoded, str):
                raise StorageException("content_base64 must be a string")
            try:
                return base64.b64decode(encoded, validate=True)
            except (binascii.Error, ValueError) as error:
                raise StorageException("content_base64 is invalid") from error
        if content is None:
            return b""
        if not isinstance(content, str):
            raise StorageException("content must be a string")
        return content.encode(cls._encoding(parameters))

    @staticmethod
    def _target(session: StorageSession) -> StorageLocation:
        target = session.context.parameters.get("target")
        if isinstance(target, StorageLocation):
            return target
        if not isinstance(target, Mapping):
            raise StorageException("target must be a StorageLocation envelope")
        return StorageLocation.from_dict(target)

    def _success(
        self,
        session: StorageSession,
        objects: Sequence[StorageObject] = (),
        metadata: Mapping[str, object] | None = None,
    ) -> StorageResult:
        return StorageResult(
            storage_id=self._descriptor.identifier,
            operation=session.context.operation,
            success=True,
            objects=tuple(objects),
            metadata={} if metadata is None else metadata,
        )

    def _failure(self, session: StorageSession, message: str) -> StorageResult:
        return StorageResult(
            storage_id=self._descriptor.identifier,
            operation=session.context.operation,
            success=False,
            message=message or "filesystem operation failed",
        )

    def _log(self, event: str, **context: object) -> None:
        self._logger.info(
            event,
            extra={"event": event, "context": context},
        )


__all__ = ["FilesystemStorage"]
