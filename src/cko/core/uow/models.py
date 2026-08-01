"""Public models for the provider-neutral Unit of Work foundation."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Callable, Mapping

from cko.core.checkpoint import CheckpointRepository
from cko.core.connectors import Connector
from cko.core.storage import Storage

from .errors import UnitOfWorkValidationError


UOW_SCHEMA_VERSION = "1.0"
UOW_VERSION = "1.0.0"
UnitOfWorkAction = Callable[[object, "UnitOfWorkContext"], object]
UnitOfWorkCompensation = Callable[
    [object, object, "UnitOfWorkContext"], object
]


class UnitOfWorkState(str, Enum):
    """Canonical Unit of Work lifecycle states."""

    CREATED = "created"
    STARTED = "started"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    CLOSED = "closed"
    FAILED = "failed"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise UnitOfWorkValidationError(
            f"{name} must be a non-empty string"
        )
    return value.strip()


def _instant(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise UnitOfWorkValidationError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise UnitOfWorkValidationError(
                "mapping numbers must be finite"
            )
        return value
    if isinstance(value, Mapping):
        normalized = {
            _text(key, "mapping key"): _freeze(item)
            for key, item in value.items()
        }
        return MappingProxyType(dict(sorted(normalized.items())))
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(item) for item in value)
    raise UnitOfWorkValidationError(
        f"unsupported metadata value: {type(value).__name__}"
    )


@dataclass(frozen=True, slots=True)
class UnitOfWorkContext:
    """Safe logical context shared by coordinated operations."""

    unit_of_work_id: str
    correlation_id: str
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = UOW_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "unit_of_work_id",
            _text(self.unit_of_work_id, "unit_of_work_id"),
        )
        object.__setattr__(
            self,
            "correlation_id",
            _text(self.correlation_id, "correlation_id"),
        )
        if not isinstance(self.metadata, Mapping):
            raise UnitOfWorkValidationError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze(self.metadata))
        if self.schema_version != UOW_SCHEMA_VERSION:
            raise UnitOfWorkValidationError(
                "unsupported UnitOfWorkContext version"
            )


@dataclass(frozen=True, slots=True)
class UnitOfWorkRepository:
    """Named registration of one already-homologated public port."""

    identifier: str
    repository: CheckpointRepository | Storage | Connector
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = UOW_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "identifier", _text(self.identifier, "identifier")
        )
        allowed = (CheckpointRepository, Storage, Connector)
        if not isinstance(self.repository, allowed):
            raise UnitOfWorkValidationError(
                "repository must implement CheckpointRepository, "
                "Storage, or Connector"
            )
        if not isinstance(self.metadata, Mapping):
            raise UnitOfWorkValidationError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze(self.metadata))
        if self.schema_version != UOW_SCHEMA_VERSION:
            raise UnitOfWorkValidationError(
                "unsupported UnitOfWorkRepository version"
            )

    @property
    def kind(self) -> str:
        """Return the registered public port family."""
        if isinstance(self.repository, CheckpointRepository):
            return "checkpoint_repository"
        if isinstance(self.repository, Storage):
            return "storage"
        return "connector"


@dataclass(frozen=True, slots=True)
class UnitOfWorkOperation:
    """One logical action and its optional compensating action."""

    operation_id: str
    repository_id: str
    action: UnitOfWorkAction
    compensation: UnitOfWorkCompensation | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = UOW_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "operation_id", _text(self.operation_id, "operation_id")
        )
        object.__setattr__(
            self,
            "repository_id",
            _text(self.repository_id, "repository_id"),
        )
        if not callable(self.action):
            raise UnitOfWorkValidationError("action must be callable")
        if self.compensation is not None and not callable(self.compensation):
            raise UnitOfWorkValidationError(
                "compensation must be callable when provided"
            )
        if not isinstance(self.metadata, Mapping):
            raise UnitOfWorkValidationError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze(self.metadata))
        if self.schema_version != UOW_SCHEMA_VERSION:
            raise UnitOfWorkValidationError(
                "unsupported UnitOfWorkOperation version"
            )


@dataclass(frozen=True, slots=True)
class UnitOfWorkResult:
    """Immutable outcome of one lifecycle or logical operation."""

    success: bool
    state: UnitOfWorkState
    event: str
    unit_of_work_id: str
    timestamp: datetime
    operation_id: str | None = None
    repository_id: str | None = None
    value: object = None
    error_code: str | None = None
    error_message: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = UOW_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise UnitOfWorkValidationError("success must be boolean")
        try:
            object.__setattr__(self, "state", UnitOfWorkState(self.state))
        except (TypeError, ValueError) as error:
            raise UnitOfWorkValidationError(
                "state must be UnitOfWorkState"
            ) from error
        object.__setattr__(self, "event", _text(self.event, "event"))
        object.__setattr__(
            self,
            "unit_of_work_id",
            _text(self.unit_of_work_id, "unit_of_work_id"),
        )
        object.__setattr__(
            self, "timestamp", _instant(self.timestamp, "timestamp")
        )
        for name in (
            "operation_id",
            "repository_id",
            "error_code",
            "error_message",
        ):
            current = getattr(self, name)
            if current is not None:
                object.__setattr__(self, name, _text(current, name))
        if self.success and (
            self.error_code is not None or self.error_message is not None
        ):
            raise UnitOfWorkValidationError(
                "successful result cannot contain an error"
            )
        if not self.success and (
            self.error_code is None or self.error_message is None
        ):
            raise UnitOfWorkValidationError(
                "failed result requires error_code and error_message"
            )
        if not isinstance(self.metadata, Mapping):
            raise UnitOfWorkValidationError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze(self.metadata))
        if self.schema_version != UOW_SCHEMA_VERSION:
            raise UnitOfWorkValidationError(
                "unsupported UnitOfWorkResult version"
            )


__all__ = [
    "UOW_SCHEMA_VERSION",
    "UOW_VERSION",
    "UnitOfWorkAction",
    "UnitOfWorkCompensation",
    "UnitOfWorkContext",
    "UnitOfWorkOperation",
    "UnitOfWorkRepository",
    "UnitOfWorkResult",
    "UnitOfWorkState",
]
