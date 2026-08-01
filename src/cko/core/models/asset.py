"""Modelo canônico e independente de infraestrutura para ativos do CKO."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any, ClassVar, Mapping, Self
from urllib.parse import urlparse

from cko.core.identity import CanonicalId
from cko.core.metadata import UniversalMetadata
from cko.core.utils import ensure_aware, require_non_empty


_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_ASSET_SCHEMA_VERSION = "1.0"


def _freeze_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    """Copia e congela recursivamente um mapa de extensão."""

    def freeze(item: object) -> object:
        if item is None or isinstance(item, (bool, int, float, str)):
            return item
        if isinstance(item, datetime):
            return ensure_aware(item)
        if isinstance(item, CanonicalId):
            return item
        if isinstance(item, Mapping):
            normalized: dict[str, object] = {}
            for key, nested in item.items():
                if not isinstance(key, str) or not key.strip():
                    raise ValueError("chaves de metadados devem ser textos não vazios")
                normalized[key] = freeze(nested)
            return MappingProxyType(normalized)
        if isinstance(item, (list, tuple)):
            return tuple(freeze(nested) for nested in item)
        raise TypeError(
            "metadados aceitam apenas valores escalares, datetime, "
            "CanonicalId, mapas e sequências"
        )

    return freeze(value)  # type: ignore[return-value]


def _primitive(value: object) -> object:
    """Converte um valor canônico em estrutura JSON estável."""
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, CanonicalId):
        return str(value)
    if isinstance(value, datetime):
        return ensure_aware(value).isoformat().replace("+00:00", "Z")
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_primitive(item) for item in value]
    if hasattr(value, "to_dict"):
        return value.to_dict()  # type: ignore[no-any-return, union-attr]
    if is_dataclass(value) and not isinstance(value, type):
        return {
            item.name: _primitive(getattr(value, item.name))
            for item in fields(value)
        }
    raise TypeError(f"valor não serializável: {type(value).__name__}")


def _to_json(value: object) -> str:
    return json.dumps(
        _primitive(value),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _datetime(value: object, field_name: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} deve ser uma data ISO 8601")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return ensure_aware(parsed)


def _optional_text(value: str | None, field_name: str) -> str | None:
    return None if value is None else require_non_empty(value, field_name)


def _positive(value: int | float | None, field_name: str) -> int | float | None:
    if value is not None and (isinstance(value, bool) or value <= 0):
        raise ValueError(f"{field_name} deve ser maior que zero")
    return value


class AssetStatus(str, Enum):
    """Disponibilidade operacional neutra de um ativo."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DELETED = "deleted"


class AssetLifecycle(str, Enum):
    """Estágio universal do ciclo de vida de um ativo."""

    DRAFT = "draft"
    REGISTERED = "registered"
    VALIDATED = "validated"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class _CanonicalEntity:
    """Semântica comum de igualdade orientada por ``CanonicalId``."""

    id: CanonicalId

    def __eq__(self, other: object) -> bool:
        return (
            type(self) is type(other)
            and self.id == other.id  # type: ignore[attr-defined]
        )

    def __hash__(self) -> int:
        return hash((type(self), self.id))


@dataclass(frozen=True, slots=True, eq=False)
class AssetFingerprint(_CanonicalEntity):
    """Assinatura de identificação não necessariamente criptográfica."""

    id: CanonicalId
    asset_id: CanonicalId
    scheme: str
    value: str
    generated_at: datetime
    attributes: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        scheme = require_non_empty(self.scheme, "scheme").lower()
        object.__setattr__(self, "scheme", scheme)
        if not _NAME_PATTERN.fullmatch(self.scheme):
            raise ValueError("scheme possui formato inválido")
        object.__setattr__(self, "value", require_non_empty(self.value, "value"))
        object.__setattr__(self, "generated_at", ensure_aware(self.generated_at))
        object.__setattr__(self, "attributes", _freeze_mapping(self.attributes))

    def to_dict(self) -> dict[str, object]:
        """Serializa a fingerprint em representação JSON compatível."""
        return {
            item.name: _primitive(getattr(self, item.name))
            for item in fields(self)
        }

    def to_json(self) -> str:
        """Serializa a fingerprint em JSON determinístico."""
        return _to_json(self)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Reconstrói e valida uma fingerprint serializada."""
        return _fingerprint(payload)  # type: ignore[return-value]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Reconstrói e valida uma fingerprint a partir de JSON."""
        return cls.from_dict(_json_object(payload))


@dataclass(frozen=True, slots=True, eq=False)
class AssetHash(_CanonicalEntity):
    """Resumo criptográfico ou checksum associado a um ativo."""

    id: CanonicalId
    asset_id: CanonicalId
    algorithm: str
    value: str
    calculated_at: datetime

    def __post_init__(self) -> None:
        algorithm = (
            require_non_empty(self.algorithm, "algorithm").lower().replace("-", "")
        )
        if not _NAME_PATTERN.fullmatch(algorithm):
            raise ValueError("algorithm possui formato inválido")
        value = require_non_empty(self.value, "value").lower()
        known_lengths = {"md5": 32, "sha1": 40, "sha256": 64, "sha512": 128}
        if algorithm in known_lengths:
            if len(value) != known_lengths[algorithm] or any(
                character not in "0123456789abcdef" for character in value
            ):
                raise ValueError(f"value não é um digest {algorithm} válido")
        object.__setattr__(self, "algorithm", algorithm)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "calculated_at", ensure_aware(self.calculated_at))

    def to_dict(self) -> dict[str, object]:
        """Serializa o hash em representação JSON compatível."""
        return {
            item.name: _primitive(getattr(self, item.name))
            for item in fields(self)
        }

    def to_json(self) -> str:
        """Serializa o hash em JSON determinístico."""
        return _to_json(self)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Reconstrói e valida um hash serializado."""
        return _hash(payload)  # type: ignore[return-value]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Reconstrói e valida um hash a partir de JSON."""
        return cls.from_dict(_json_object(payload))


@dataclass(frozen=True, slots=True, eq=False)
class AssetClassification(_CanonicalEntity):
    """Classificação atribuída por uma taxonomia identificada, sem motor embutido."""

    id: CanonicalId
    asset_id: CanonicalId
    scheme: str
    value: str
    assigned_at: datetime
    confidence: float | None = None
    attributes: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "scheme", require_non_empty(self.scheme, "scheme"))
        object.__setattr__(self, "value", require_non_empty(self.value, "value"))
        object.__setattr__(self, "assigned_at", ensure_aware(self.assigned_at))
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence deve estar entre 0.0 e 1.0")
        object.__setattr__(self, "attributes", _freeze_mapping(self.attributes))

    def to_dict(self) -> dict[str, object]:
        """Serializa a classificação em representação JSON compatível."""
        return {
            item.name: _primitive(getattr(self, item.name))
            for item in fields(self)
        }

    def to_json(self) -> str:
        """Serializa a classificação em JSON determinístico."""
        return _to_json(self)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Reconstrói e valida uma classificação serializada."""
        return _classification(payload)  # type: ignore[return-value]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Reconstrói e valida uma classificação a partir de JSON."""
        return cls.from_dict(_json_object(payload))


@dataclass(frozen=True, slots=True, eq=False)
class AssetRelation(_CanonicalEntity):
    """Relação semântica identificada entre dois ativos canônicos."""

    id: CanonicalId
    source_asset_id: CanonicalId
    target_asset_id: CanonicalId
    relation_type: str
    created_at: datetime
    directed: bool = True
    attributes: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.source_asset_id == self.target_asset_id:
            raise ValueError("uma relação deve conectar ativos distintos")
        object.__setattr__(
            self,
            "relation_type",
            require_non_empty(self.relation_type, "relation_type"),
        )
        object.__setattr__(self, "created_at", ensure_aware(self.created_at))
        object.__setattr__(self, "attributes", _freeze_mapping(self.attributes))

    def to_dict(self) -> dict[str, object]:
        """Serializa a relação em representação JSON compatível."""
        return {
            item.name: _primitive(getattr(self, item.name))
            for item in fields(self)
        }

    def to_json(self) -> str:
        """Serializa a relação em JSON determinístico."""
        return _to_json(self)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Reconstrói e valida uma relação serializada."""
        return _relation(payload)  # type: ignore[return-value]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Reconstrói e valida uma relação a partir de JSON."""
        return cls.from_dict(_json_object(payload))


@dataclass(frozen=True, slots=True, eq=False)
class Asset(_CanonicalEntity):
    """Entidade raiz para qualquer ativo reutilizável do ecossistema CKO."""

    kind: ClassVar[str] = "asset"

    id: CanonicalId
    name: str
    metadata: UniversalMetadata
    created_at: datetime
    updated_at: datetime
    status: AssetStatus = AssetStatus.ACTIVE
    lifecycle: AssetLifecycle = AssetLifecycle.REGISTERED
    classifications: tuple[AssetClassification, ...] = ()
    fingerprints: tuple[AssetFingerprint, ...] = ()
    hashes: tuple[AssetHash, ...] = ()
    attributes: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.id, CanonicalId):
            raise TypeError("id deve ser CanonicalId")
        if not isinstance(self.metadata, UniversalMetadata):
            raise TypeError("metadata deve ser UniversalMetadata")
        object.__setattr__(
            self,
            "metadata",
            UniversalMetadata(
                media_type=self.metadata.media_type,
                created_at=self.metadata.created_at,
                modified_at=self.metadata.modified_at,
                language=self.metadata.language,
                attributes=_freeze_mapping(self.metadata.attributes),
            ),
        )
        object.__setattr__(self, "name", require_non_empty(self.name, "name"))
        created_at = ensure_aware(self.created_at)
        updated_at = ensure_aware(self.updated_at)
        if updated_at < created_at:
            raise ValueError("updated_at não pode anteceder created_at")
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "updated_at", updated_at)
        object.__setattr__(self, "status", AssetStatus(self.status))
        object.__setattr__(self, "lifecycle", AssetLifecycle(self.lifecycle))
        for field_name in ("classifications", "fingerprints", "hashes"):
            values = tuple(getattr(self, field_name))
            if any(value.asset_id != self.id for value in values):
                raise ValueError(f"{field_name} deve referenciar o id do ativo")
            object.__setattr__(self, field_name, values)
        object.__setattr__(self, "attributes", _freeze_mapping(self.attributes))

    def to_dict(self) -> dict[str, object]:
        """Serializa o ativo no envelope canônico versionado."""
        payload = {
            item.name: _primitive(getattr(self, item.name))
            for item in fields(self)
        }
        return {
            "schema_version": _ASSET_SCHEMA_VERSION,
            "kind": self.kind,
            **payload,
        }

    def to_json(self) -> str:
        """Serializa o ativo em JSON UTF-8 lógico e determinístico."""
        return _to_json(self)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Reconstrói e valida um ativo da representação canônica."""
        asset = asset_from_dict(payload)
        if not isinstance(asset, cls):
            raise ValueError(f"payload representa {asset.kind}, não {cls.kind}")
        return asset

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Reconstrói e valida um ativo a partir de JSON."""
        decoded = json.loads(payload)
        if not isinstance(decoded, dict):
            raise ValueError("JSON de ativo deve conter um objeto")
        return cls.from_dict(decoded)


@dataclass(frozen=True, slots=True, eq=False)
class DocumentAsset(Asset):
    """Documento textual ou paginado, sem vínculo com parser ou OCR."""

    kind: ClassVar[str] = "document"
    page_count: int | None = None

    def __post_init__(self) -> None:
        super(DocumentAsset, self).__post_init__()
        object.__setattr__(self, "page_count", _positive(self.page_count, "page_count"))


@dataclass(frozen=True, slots=True, eq=False)
class ImageAsset(Asset):
    """Imagem descrita somente por propriedades canônicas."""

    kind: ClassVar[str] = "image"
    width: int | None = None
    height: int | None = None

    def __post_init__(self) -> None:
        super(ImageAsset, self).__post_init__()
        object.__setattr__(self, "width", _positive(self.width, "width"))
        object.__setattr__(self, "height", _positive(self.height, "height"))


@dataclass(frozen=True, slots=True, eq=False)
class AudioAsset(Asset):
    """Áudio descrito sem codec, stream ou infraestrutura de leitura."""

    kind: ClassVar[str] = "audio"
    duration_seconds: float | None = None

    def __post_init__(self) -> None:
        super(AudioAsset, self).__post_init__()
        object.__setattr__(
            self,
            "duration_seconds",
            _positive(self.duration_seconds, "duration_seconds"),
        )


@dataclass(frozen=True, slots=True, eq=False)
class VideoAsset(Asset):
    """Vídeo descrito sem codec, stream ou infraestrutura de leitura."""

    kind: ClassVar[str] = "video"
    duration_seconds: float | None = None
    width: int | None = None
    height: int | None = None

    def __post_init__(self) -> None:
        super(VideoAsset, self).__post_init__()
        for field_name in ("duration_seconds", "width", "height"):
            object.__setattr__(
                self,
                field_name,
                _positive(getattr(self, field_name), field_name),
            )


@dataclass(frozen=True, slots=True, eq=False)
class ProjectAsset(Asset):
    """Projeto lógico independente de ferramenta de gestão ou repositório."""

    kind: ClassVar[str] = "project"
    project_code: str | None = None

    def __post_init__(self) -> None:
        super(ProjectAsset, self).__post_init__()
        object.__setattr__(
            self,
            "project_code",
            _optional_text(self.project_code, "project_code"),
        )


@dataclass(frozen=True, slots=True, eq=False)
class DatabaseAsset(Asset):
    """Base de dados como ativo lógico, sem conexão ou persistência."""

    kind: ClassVar[str] = "database"
    database_system: str | None = None
    schema_name: str | None = None

    def __post_init__(self) -> None:
        super(DatabaseAsset, self).__post_init__()
        for field_name in ("database_system", "schema_name"):
            object.__setattr__(
                self,
                field_name,
                _optional_text(getattr(self, field_name), field_name),
            )


@dataclass(frozen=True, slots=True, eq=False)
class KnowledgeAsset(Asset):
    """Unidade de conhecimento neutra, sem RAG, embeddings ou grafo."""

    kind: ClassVar[str] = "knowledge"
    knowledge_type: str | None = None

    def __post_init__(self) -> None:
        super(KnowledgeAsset, self).__post_init__()
        object.__setattr__(
            self,
            "knowledge_type",
            _optional_text(self.knowledge_type, "knowledge_type"),
        )


@dataclass(frozen=True, slots=True, eq=False)
class FolderAsset(Asset):
    """Contêiner lógico de ativos, sem representar caminho de filesystem."""

    kind: ClassVar[str] = "folder"


@dataclass(frozen=True, slots=True, eq=False)
class ReferenceAsset(Asset):
    """Referência canônica a outro ativo ou identificador URI."""

    kind: ClassVar[str] = "reference"
    target_asset_id: CanonicalId | None = None
    target_uri: str | None = None
    reference_type: str = "reference"

    def __post_init__(self) -> None:
        super(ReferenceAsset, self).__post_init__()
        if self.target_asset_id is None and self.target_uri is None:
            raise ValueError("reference requer target_asset_id ou target_uri")
        if self.target_uri is not None:
            uri = require_non_empty(self.target_uri, "target_uri")
            if not urlparse(uri).scheme:
                raise ValueError("target_uri deve possuir esquema explícito")
            object.__setattr__(self, "target_uri", uri)
        object.__setattr__(
            self,
            "reference_type",
            require_non_empty(self.reference_type, "reference_type"),
        )


_ASSET_TYPES: dict[str, type[Asset]] = {
    asset_type.kind: asset_type
    for asset_type in (
        Asset,
        DocumentAsset,
        ImageAsset,
        AudioAsset,
        VideoAsset,
        ProjectAsset,
        DatabaseAsset,
        KnowledgeAsset,
        FolderAsset,
        ReferenceAsset,
    )
}


def _metadata(payload: object) -> UniversalMetadata:
    if not isinstance(payload, Mapping):
        raise ValueError("metadata deve ser um objeto")
    return UniversalMetadata(
        media_type=str(payload["media_type"]),
        created_at=_datetime(payload["created_at"], "metadata.created_at"),
        modified_at=_datetime(payload["modified_at"], "metadata.modified_at"),
        language=(
            None
            if payload.get("language") is None
            else str(payload["language"])
        ),
        attributes=payload.get("attributes", {}),  # type: ignore[arg-type]
    )


def _json_object(payload: str) -> Mapping[str, object]:
    decoded = json.loads(payload)
    if not isinstance(decoded, dict):
        raise ValueError("JSON canônico deve conter um objeto")
    return decoded


def _classification(payload: object) -> AssetClassification:
    if not isinstance(payload, Mapping):
        raise ValueError("classification deve ser um objeto")
    confidence = payload.get("confidence")
    return AssetClassification(
        id=CanonicalId.parse(str(payload["id"])),
        asset_id=CanonicalId.parse(str(payload["asset_id"])),
        scheme=str(payload["scheme"]),
        value=str(payload["value"]),
        assigned_at=_datetime(payload["assigned_at"], "assigned_at"),
        confidence=None if confidence is None else float(confidence),
        attributes=payload.get("attributes", {}),  # type: ignore[arg-type]
    )


def _fingerprint(payload: object) -> AssetFingerprint:
    if not isinstance(payload, Mapping):
        raise ValueError("fingerprint deve ser um objeto")
    return AssetFingerprint(
        id=CanonicalId.parse(str(payload["id"])),
        asset_id=CanonicalId.parse(str(payload["asset_id"])),
        scheme=str(payload["scheme"]),
        value=str(payload["value"]),
        generated_at=_datetime(payload["generated_at"], "generated_at"),
        attributes=payload.get("attributes", {}),  # type: ignore[arg-type]
    )


def _hash(payload: object) -> AssetHash:
    if not isinstance(payload, Mapping):
        raise ValueError("hash deve ser um objeto")
    return AssetHash(
        id=CanonicalId.parse(str(payload["id"])),
        asset_id=CanonicalId.parse(str(payload["asset_id"])),
        algorithm=str(payload["algorithm"]),
        value=str(payload["value"]),
        calculated_at=_datetime(payload["calculated_at"], "calculated_at"),
    )


def _relation(payload: object) -> AssetRelation:
    if not isinstance(payload, Mapping):
        raise ValueError("relation deve ser um objeto")
    return AssetRelation(
        id=CanonicalId.parse(str(payload["id"])),
        source_asset_id=CanonicalId.parse(str(payload["source_asset_id"])),
        target_asset_id=CanonicalId.parse(str(payload["target_asset_id"])),
        relation_type=str(payload["relation_type"]),
        created_at=_datetime(payload["created_at"], "created_at"),
        directed=bool(payload.get("directed", True)),
        attributes=payload.get("attributes", {}),  # type: ignore[arg-type]
    )


def asset_from_dict(payload: Mapping[str, object]) -> Asset:
    """Reconstrói um subtipo de ativo pelo discriminador canônico ``kind``."""
    if payload.get("schema_version") != _ASSET_SCHEMA_VERSION:
        raise ValueError("schema_version de ativo não suportada")
    kind = payload.get("kind")
    if not isinstance(kind, str) or kind not in _ASSET_TYPES:
        raise ValueError("kind de ativo não suportado")
    asset_type = _ASSET_TYPES[kind]
    common_names = {item.name for item in fields(Asset)}
    type_names = {item.name for item in fields(asset_type)}
    allowed = type_names | {"kind", "schema_version"}
    unknown = set(payload) - allowed
    if unknown:
        raise ValueError(f"campos desconhecidos: {', '.join(sorted(unknown))}")
    common: dict[str, Any] = {
        "id": CanonicalId.parse(str(payload["id"])),
        "name": str(payload["name"]),
        "metadata": _metadata(payload["metadata"]),
        "created_at": _datetime(payload["created_at"], "created_at"),
        "updated_at": _datetime(payload["updated_at"], "updated_at"),
        "status": AssetStatus(str(payload["status"])),
        "lifecycle": AssetLifecycle(str(payload["lifecycle"])),
        "classifications": tuple(
            _classification(item)
            for item in payload.get("classifications", [])  # type: ignore[union-attr]
        ),
        "fingerprints": tuple(
            _fingerprint(item)
            for item in payload.get("fingerprints", [])  # type: ignore[union-attr]
        ),
        "hashes": tuple(
            _hash(item)
            for item in payload.get("hashes", [])  # type: ignore[union-attr]
        ),
        "attributes": payload.get("attributes", {}),
    }
    extras = {
        name: payload[name]
        for name in type_names - common_names
        if name in payload
    }
    if "target_asset_id" in extras and extras["target_asset_id"] is not None:
        extras["target_asset_id"] = CanonicalId.parse(str(extras["target_asset_id"]))
    return asset_type(**common, **extras)


__all__ = [
    "Asset",
    "AssetClassification",
    "AssetFingerprint",
    "AssetHash",
    "AssetLifecycle",
    "AssetRelation",
    "AssetStatus",
    "AudioAsset",
    "DatabaseAsset",
    "DocumentAsset",
    "FolderAsset",
    "ImageAsset",
    "KnowledgeAsset",
    "ProjectAsset",
    "ReferenceAsset",
    "VideoAsset",
    "asset_from_dict",
]
