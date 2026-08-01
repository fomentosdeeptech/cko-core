"""Complete model and aggregate validator for Knowledge Objects."""

from __future__ import annotations

import hashlib
import json
from dataclasses import is_dataclass

from .contracts import SerializableKnowledgeModel, primitive
from .errors import KnowledgeValidationError
from .models import KnowledgeCollection, KnowledgeObject


class KnowledgeObjectValidator:
    """Validate structural, immutable, identity, relationship, and lineage rules."""

    def validate(self, value: SerializableKnowledgeModel) -> None:
        if not isinstance(value, SerializableKnowledgeModel) or not is_dataclass(value):
            raise KnowledgeValidationError("value must be a canonical knowledge dataclass")
        value._validate_schema()
        params = getattr(type(value), "__dataclass_params__", None)
        if params is None or not params.frozen or not hasattr(type(value), "__slots__"):
            raise KnowledgeValidationError("knowledge models must be frozen and slotted")
        if value.model != type(value).model_name:
            raise KnowledgeValidationError("invalid model discriminator")
        if isinstance(value, KnowledgeObject):
            self._validate_object(value)
        elif isinstance(value, KnowledgeCollection):
            for item in value.objects:
                self._validate_object(item)

    def _validate_object(self, value: KnowledgeObject) -> None:
        identity = value.identity
        if identity.version != value.version.version:
            raise KnowledgeValidationError("identity and version mismatch")
        content_bytes = json.dumps(
            primitive(value.content), ensure_ascii=False, allow_nan=False,
            sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
        if hashlib.sha256(content_bytes).hexdigest() != value.version.hash:
            raise KnowledgeValidationError("version hash does not match content")
        relationship_ids = [item.relationship_id for item in value.relationships]
        if len(relationship_ids) != len(set(relationship_ids)):
            raise KnowledgeValidationError("duplicate relationships")
        reference_ids = [item.reference_id for item in value.content.references]
        if len(reference_ids) != len(set(reference_ids)):
            raise KnowledgeValidationError("duplicate references")
        if any(item.target_object_id == identity.logical_id for item in value.content.references):
            raise KnowledgeValidationError("self references are invalid")


__all__ = ["KnowledgeObjectValidator"]
