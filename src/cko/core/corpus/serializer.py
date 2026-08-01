"""Closed-schema canonical UTF-8 JSON serialization for knowledge corpora."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Mapping
from uuid import UUID

from .contracts import CORPUS_SCHEMA_VERSION, CorpusModel
from .enums import CorpusMemberCategory
from .errors import CorpusSerializationError
from .factory import CorpusFactory
from .identity import CorpusId, CorpusIdentity
from .models import (CorpusComparisonResult, CorpusManifest, CorpusMemberReference,
                     CorpusMetadata, CorpusReferenceChange, CorpusSnapshot,
                     CorpusStatistics, CorpusVersion, KnowledgeCorpus)

_CLASSES = (CorpusId, CorpusIdentity, CorpusVersion, CorpusMemberReference,
            CorpusManifest, CorpusMetadata, KnowledgeCorpus, CorpusStatistics,
            CorpusReferenceChange, CorpusComparisonResult, CorpusSnapshot)
_MODELS = {kind.discriminator for kind in _CLASSES}


def _strict(value: object, model: str, names: set[str]) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != names | {"model", "schema_version"}:
        raise CorpusSerializationError(f"invalid or unknown {model} fields")
    if value.get("model") != model:
        raise CorpusSerializationError(f"invalid {model} discriminator")
    if value.get("schema_version") != CORPUS_SCHEMA_VERSION:
        raise CorpusSerializationError(f"unsupported {model} schema_version")
    return value


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise CorpusSerializationError("expected JSON object")
    return value


def _array(value: object) -> list[object]:
    if not isinstance(value, list):
        raise CorpusSerializationError("expected JSON array")
    return value


class DeterministicCorpusSerializer:
    def __init__(self, factory: CorpusFactory | None = None) -> None:
        self._factory = factory or CorpusFactory()

    def serialize(self, value: CorpusModel) -> bytes:
        if not isinstance(value, CorpusModel) or value.model not in _MODELS:
            raise CorpusSerializationError("unknown corpus model")
        try:
            return json.dumps(value.to_dict(), ensure_ascii=False, allow_nan=False,
                              sort_keys=True, separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError) as error:
            raise CorpusSerializationError("corpus model is not serializable") from error

    def digest(self, value: CorpusModel) -> str:
        return hashlib.sha256(self.serialize(value)).hexdigest()

    def deserialize(self, payload: bytes | str) -> CorpusModel:
        if isinstance(payload, bytes):
            try:
                raw = payload.decode("utf-8")
            except UnicodeDecodeError as error:
                raise CorpusSerializationError("payload must be UTF-8") from error
        elif isinstance(payload, str):
            raw = payload
        else:
            raise CorpusSerializationError("payload must be bytes or string")
        try:
            value = json.loads(raw, parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
        except (json.JSONDecodeError, ValueError) as error:
            raise CorpusSerializationError("payload must be valid JSON") from error
        canonical = json.dumps(value, ensure_ascii=False, allow_nan=False,
                               sort_keys=True, separators=(",", ":"))
        if raw != canonical:
            raise CorpusSerializationError("payload is not canonical JSON")
        try:
            return self._decode(value)
        except CorpusSerializationError:
            raise
        except (TypeError, ValueError, KeyError) as error:
            raise CorpusSerializationError("serialized corpus structure is invalid") from error

    def _plain(self, value: object) -> object:
        if isinstance(value, Mapping):
            if "model" in value:
                return self._decode(value)
            return {str(key): self._plain(item) for key, item in value.items()}
        if isinstance(value, list):
            return tuple(self._plain(item) for item in value)
        return value

    def _decode(self, payload: object) -> CorpusModel:
        if not isinstance(payload, Mapping) or not isinstance(payload.get("model"), str):
            raise CorpusSerializationError("model discriminator is required")
        model = payload["model"]
        if model not in _MODELS:
            raise CorpusSerializationError(f"unknown model discriminator: {model}")
        nested = self._decode
        if model == "corpus_id":
            value = _strict(payload, model, {"value"})
            return CorpusId(UUID(str(value["value"])))
        if model == "corpus_identity":
            value = _strict(payload, model, {"corpus_id", "namespace", "name"})
            return CorpusIdentity(nested(value["corpus_id"]), value["namespace"], value["name"])  # type: ignore[arg-type]
        if model == "corpus_version":
            value = _strict(payload, model, {"version", "revision"})
            return CorpusVersion(value["version"], value["revision"])  # type: ignore[arg-type]
        if model == "corpus_member_reference":
            value = _strict(payload, model, {"member_id", "category", "member_version",
                "discriminator_name", "namespace", "member_digest", "attributes"})
            return CorpusMemberReference(value["member_id"], CorpusMemberCategory(value["category"]),
                value["member_version"], value["discriminator_name"], value["namespace"],
                value["member_digest"], self._plain(_mapping(value["attributes"])))  # type: ignore[arg-type]
        if model == "corpus_manifest":
            value = _strict(payload, model, {"members"})
            return CorpusManifest(tuple(nested(item) for item in _array(value["members"])))  # type: ignore[arg-type]
        if model == "corpus_metadata":
            value = _strict(payload, model, {"description", "labels", "attributes"})
            return CorpusMetadata(value["description"], tuple(_array(value["labels"])),
                                  self._plain(_mapping(value["attributes"])))  # type: ignore[arg-type]
        if model == "knowledge_corpus":
            value = _strict(payload, model, {"identity", "corpus_version", "manifest",
                "metadata", "digest", "serialization_version"})
            if value["serialization_version"] != "1.0":
                raise CorpusSerializationError("unsupported serialization_version")
            return self._factory.from_parts(identity=nested(value["identity"]),
                corpus_version=nested(value["corpus_version"]), manifest=nested(value["manifest"]),
                metadata=nested(value["metadata"]), digest=value["digest"])  # type: ignore[arg-type]
        if model == "corpus_statistics":
            value = _strict(payload, model, {"total_members", "members_with_digest",
                "categories_present", "by_category", "by_member_version"})
            return CorpusStatistics(value["total_members"], value["members_with_digest"],
                value["categories_present"], self._plain(_mapping(value["by_category"])),
                self._plain(_mapping(value["by_member_version"])))  # type: ignore[arg-type]
        if model == "corpus_reference_change":
            value = _strict(payload, model, {"before", "after", "version_changed", "digest_changed"})
            return CorpusReferenceChange(nested(value["before"]), nested(value["after"]),
                value["version_changed"], value["digest_changed"])  # type: ignore[arg-type]
        if model == "corpus_comparison_result":
            value = _strict(payload, model, {"added", "removed", "preserved", "changed"})
            return CorpusComparisonResult(tuple(nested(item) for item in _array(value["added"])),
                tuple(nested(item) for item in _array(value["removed"])),
                tuple(nested(item) for item in _array(value["preserved"])),
                tuple(nested(item) for item in _array(value["changed"])))  # type: ignore[arg-type]
        if model == "corpus_snapshot":
            value = _strict(payload, model, {"snapshot_id", "corpus_id", "corpus_version",
                "manifest", "digest", "statistics", "captured_at"})
            try:
                captured = datetime.fromisoformat(str(value["captured_at"]))
            except (TypeError, ValueError) as error:
                raise CorpusSerializationError("invalid ISO-8601 datetime") from error
            return CorpusSnapshot(nested(value["snapshot_id"]), nested(value["corpus_id"]),
                nested(value["corpus_version"]), nested(value["manifest"]), value["digest"],
                nested(value["statistics"]), captured)  # type: ignore[arg-type]
        raise CorpusSerializationError("unknown model discriminator")


__all__ = ["DeterministicCorpusSerializer"]
