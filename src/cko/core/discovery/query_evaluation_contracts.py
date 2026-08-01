"""Public contracts for infrastructure-neutral query evaluation."""

from __future__ import annotations

from collections.abc import AsyncIterable, Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol, runtime_checkable

from .cancellation import CancellationToken
from .query_models import QueryPlan


@dataclass(frozen=True, slots=True)
class AttributeValue:
    """Result of safely resolving one logical attribute path."""

    attribute: str
    exists: bool
    value: object = None
    logical_path: tuple[str, ...] = ()


@runtime_checkable
class QueryEvaluationSubject(Protocol):
    """Object exposed to evaluation without a storage-specific shape."""

    @property
    def logical_identity(self) -> str | None:
        """Return the stable logical identity, when declared."""

    @property
    def source(self) -> object:
        """Return the in-memory value exposed to the attribute resolver."""


@runtime_checkable
class AttributeResolver(Protocol):
    """Resolve public logical paths without invoking arbitrary methods."""

    def resolve(self, subject: object, attribute: str) -> AttributeValue:
        """Resolve one logical attribute from an in-memory subject."""


@runtime_checkable
class QueryEvaluationStream(Protocol):
    """Incrementally evaluate synchronous or asynchronous subjects."""

    def evaluate(
        self,
        plan: QueryPlan,
        subjects: Iterable[QueryEvaluationSubject],
        *,
        cancellation_token: CancellationToken | None = None,
    ) -> object:
        """Evaluate a synchronous stream using the configured engine."""

    async def evaluate_async(
        self,
        plan: QueryPlan,
        subjects: AsyncIterable[QueryEvaluationSubject],
        *,
        cancellation_token: CancellationToken | None = None,
    ) -> object:
        """Evaluate an asynchronous stream using the configured engine."""


@dataclass(frozen=True, slots=True, init=False)
class MappingQueryEvaluationSubject:
    """Neutral immutable evaluation subject backed by a string-keyed mapping."""

    values: Mapping[str, object]
    identity: str | None

    def __init__(
        self,
        values: Mapping[str, object],
        identity: str | None = None,
    ) -> None:
        if not isinstance(values, Mapping):
            raise TypeError("values must be a mapping")
        copied: dict[str, object] = {}
        for key, value in values.items():
            if not isinstance(key, str) or not key or key.startswith("_"):
                raise ValueError("subject keys must be public non-empty strings")
            copied[key] = value
        inferred = identity
        if inferred is None:
            for key in ("logical_identity", "canonical_id", "id"):
                candidate = copied.get(key)
                if candidate is not None:
                    inferred = str(candidate)
                    break
        if inferred is not None and not str(inferred).strip():
            raise ValueError("identity must be non-empty when declared")
        object.__setattr__(self, "values", MappingProxyType(copied))
        object.__setattr__(
            self, "identity", str(inferred).strip() if inferred is not None else None
        )

    @property
    def logical_identity(self) -> str | None:
        """Return the explicit or conventionally inferred stable identity."""
        return self.identity

    @property
    def source(self) -> object:
        """Return the immutable mapping exposed for logical resolution."""
        return self.values


__all__ = [
    "AttributeResolver",
    "AttributeValue",
    "MappingQueryEvaluationSubject",
    "QueryEvaluationStream",
    "QueryEvaluationSubject",
]
