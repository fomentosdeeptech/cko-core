"""Stable exception hierarchy for the Knowledge Graph Foundation."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from cko.core.exceptions import CKOError


class GraphError(CKOError):
    """Base error emitted by the technology-neutral graph boundary."""

    default_code = "graph_error"

    def __init__(self, message: str, *, code: str | None = None,
                 model: str | None = None,
                 details: Mapping[str, object] | None = None) -> None:
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message must be a non-empty string")
        selected_code = code or self.default_code
        if not isinstance(selected_code, str) or not selected_code.strip():
            raise ValueError("code must be a non-empty string")
        if model is not None and (not isinstance(model, str) or not model.strip()):
            raise ValueError("model must be a non-empty string")
        if details is not None and not isinstance(details, Mapping):
            raise ValueError("details must be a mapping")
        super().__init__(message.strip())
        self.code = selected_code.strip()
        self.model = None if model is None else model.strip()
        self.details = MappingProxyType(dict(details or {}))

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": str(self), "model": self.model,
                "details": dict(self.details)}


class GraphValidationError(GraphError, ValueError):
    default_code = "graph_validation_error"


class GraphSerializationError(GraphError):
    default_code = "graph_serialization_error"


class GraphFactoryError(GraphError):
    default_code = "graph_factory_error"


class GraphIdentityError(GraphValidationError):
    default_code = "graph_identity_error"


class GraphNavigationError(GraphError):
    default_code = "graph_navigation_error"


class GraphIndexError(GraphError):
    default_code = "graph_index_error"


__all__ = [
    "GraphError", "GraphFactoryError", "GraphIdentityError", "GraphIndexError",
    "GraphNavigationError", "GraphSerializationError", "GraphValidationError",
]
