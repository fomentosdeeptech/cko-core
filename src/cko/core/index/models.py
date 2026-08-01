"""Canonical immutable models for deterministic in-memory indexes."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import ClassVar, Mapping
from uuid import UUID

from .contracts import (INDEX_SCHEMA_VERSION, IndexModel, deep_freeze, instant,
                        non_negative, primitive, semantic_version, text)
from .enums import (IndexConsistency, IndexKeyType, IndexMultiplicity,
                    IndexOperationType, IndexOrdering, IndexSnapshotType,
                    IndexStatus, IndexTarget, IndexType, IndexValuePolicy)
from .errors import (IndexDefinitionError, IndexFactoryError, IndexQueryError,
                     IndexValidationError)
from .identity import IndexId, IndexIdentity
from .metadata import IndexMetadata

_FACTORY_TOKEN=object()
_PATH=re.compile(r"^[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)*$")
_ROOTS={"identity","namespace","type","document_type","relationship_type","node_type",
        "status","category","author","creator","organization","source","language",
        "version","tags","keywords","attributes","properties","created_at","updated_at","checksum"}


def _enum(value: object, kind: type[Enum], name: str):
    try: return kind(value)
    except (TypeError,ValueError) as error: raise IndexValidationError(f"{name} contains an invalid enum") from error


def _digest_payload(value: object) -> str:
    raw=json.dumps(primitive(value),ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class IndexKey(IndexModel):
    value: object
    key_type: IndexKeyType | None = None
    schema_version: str = INDEX_SCHEMA_VERSION
    discriminator: ClassVar[str] = "index_key"
    def __post_init__(self) -> None:
        value=self.value; selected=self.key_type
        if selected is not None: selected=_enum(selected,IndexKeyType,"key_type")
        if value is None: inferred=IndexKeyType.NULL
        elif isinstance(value,bool): inferred=IndexKeyType.BOOLEAN
        elif isinstance(value,int): inferred=IndexKeyType.INTEGER
        elif isinstance(value,(float,Decimal)):
            if not math.isfinite(float(value)): raise IndexValidationError("index key numbers must be finite")
            inferred=IndexKeyType.DECIMAL; value=Decimal(str(value)).normalize()
        elif isinstance(value,UUID): inferred=IndexKeyType.UUID
        elif isinstance(value,datetime): inferred=IndexKeyType.DATETIME; value=instant(value,"key")
        elif isinstance(value,Enum): inferred=IndexKeyType.ENUM; value=value.value
        elif isinstance(value,str): inferred=IndexKeyType.TEXT
        elif isinstance(value,(tuple,list)):
            if not value: raise IndexValidationError("sequence keys must not be empty")
            normalized=tuple(IndexKey(item) for item in value)
            if any(item.key_type is IndexKeyType.SEQUENCE for item in normalized): raise IndexValidationError("nested sequence keys are not supported")
            inferred=IndexKeyType.SEQUENCE; value=tuple(item.value for item in normalized)
        else: raise IndexValidationError(f"unsupported index key value: {type(value).__name__}")
        if selected is IndexKeyType.SHA256:
            if not isinstance(value,str) or re.fullmatch(r"[0-9a-fA-F]{64}",value) is None: raise IndexValidationError("SHA-256 key must contain 64 hexadecimal characters")
            value=value.lower(); inferred=IndexKeyType.SHA256
        elif selected is not None and selected is not inferred: raise IndexValidationError("key_type does not match value")
        object.__setattr__(self,"value",value); object.__setattr__(self,"key_type",inferred); self._validate_schema()
    @property
    def sort_token(self) -> str:
        """Stable total-order token: type first, then canonical scalar value."""
        encoded = self.to_dict()["value"]
        return f"{self.key_type.value}:"+json.dumps(encoded,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    def to_dict(self) -> dict[str,object]:
        encoded = ([IndexKey(item).to_dict() for item in self.value]
                   if self.key_type is IndexKeyType.SEQUENCE else primitive(self.value))
        return {"schema_version":self.schema_version,"model":self.model,
                "value":encoded,"key_type":self.key_type.value}


@dataclass(frozen=True, slots=True)
class IndexReference(IndexModel):
    namespace: str
    canonical_id: str
    entity_type: IndexTarget
    version: str
    entity_discriminator: str
    checksum: str | None = None
    metadata: Mapping[str,object] = field(default_factory=dict)
    schema_version: str = INDEX_SCHEMA_VERSION
    discriminator: ClassVar[str] = "index_reference"
    def __post_init__(self) -> None:
        object.__setattr__(self,"namespace",text(self.namespace,"namespace")); object.__setattr__(self,"canonical_id",text(self.canonical_id,"canonical_id"))
        object.__setattr__(self,"entity_type",_enum(self.entity_type,IndexTarget,"entity_type")); object.__setattr__(self,"version",semantic_version(self.version))
        object.__setattr__(self,"entity_discriminator",text(self.entity_discriminator,"entity_discriminator"))
        if self.checksum is not None:
            checksum=text(self.checksum,"checksum"); assert isinstance(checksum,str)
            if re.fullmatch(r"[0-9a-fA-F]{64}",checksum) is None: raise IndexValidationError("checksum must be SHA-256")
            object.__setattr__(self,"checksum",checksum.lower())
        object.__setattr__(self,"metadata",deep_freeze(self.metadata)); self._validate_schema()
    @property
    def sort_token(self) -> tuple[str,...]: return (self.entity_type.value,self.namespace,self.canonical_id,self.version)


@dataclass(frozen=True, slots=True)
class IndexField(IndexModel):
    path: str
    key_type: IndexKeyType | None = None
    required: bool = True
    schema_version: str = INDEX_SCHEMA_VERSION
    discriminator: ClassVar[str] = "index_field"
    def __post_init__(self) -> None:
        path=text(self.path,"path"); assert isinstance(path,str)
        if not _PATH.fullmatch(path): raise IndexDefinitionError("field path uses an invalid logical grammar")
        root=path.split(".",1)[0]
        if root not in _ROOTS: raise IndexDefinitionError("field is not an indexable dimension")
        if root in {"attributes","properties"} and "." not in path: raise IndexDefinitionError("attribute/property field requires a named path")
        object.__setattr__(self,"path",path)
        if self.key_type is not None: object.__setattr__(self,"key_type",_enum(self.key_type,IndexKeyType,"key_type"))
        if not isinstance(self.required,bool): raise IndexValidationError("required must be boolean")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class IndexDefinition(IndexModel):
    definition_id: IndexId
    name: str
    namespace: str
    index_type: IndexType
    targets: tuple[IndexTarget,...]
    fields: tuple[IndexField,...]
    unique: bool=False
    multiplicity: IndexMultiplicity=IndexMultiplicity.SINGLE
    normalization: str="canonical"
    case_sensitive: bool=True
    missing_value_policy: IndexValuePolicy=IndexValuePolicy.REJECT
    multiple_value_policy: IndexValuePolicy=IndexValuePolicy.REJECT
    status: IndexStatus=IndexStatus.ACTIVE
    version: str="1.0.0"
    description: str | None=None
    metadata: Mapping[str,object]=field(default_factory=dict)
    schema_version: str=INDEX_SCHEMA_VERSION
    _factory_token: InitVar[object|None]=None
    discriminator: ClassVar[str]="index_definition"
    def __post_init__(self,_factory_token:object|None)->None:
        if _factory_token is not _FACTORY_TOKEN: raise IndexFactoryError("IndexDefinition must be created by IndexFactory")
        if not isinstance(self.definition_id,IndexId): raise IndexDefinitionError("definition_id must be IndexId")
        object.__setattr__(self,"name",text(self.name,"name")); object.__setattr__(self,"namespace",text(self.namespace,"namespace"))
        object.__setattr__(self,"index_type",_enum(self.index_type,IndexType,"index_type"))
        targets=tuple(_enum(v,IndexTarget,"targets") for v in self.targets); fields=tuple(self.fields)
        if not targets or len(targets)!=len(set(targets)): raise IndexDefinitionError("targets must be non-empty and unique")
        if not fields or any(not isinstance(v,IndexField) for v in fields): raise IndexDefinitionError("fields must contain IndexField values")
        if len({v.path for v in fields})!=len(fields): raise IndexDefinitionError("field paths must be unique")
        object.__setattr__(self,"targets",tuple(sorted(targets,key=lambda v:v.value))); object.__setattr__(self,"fields",tuple(sorted(fields,key=lambda v:v.path)))
        object.__setattr__(self,"multiplicity",_enum(self.multiplicity,IndexMultiplicity,"multiplicity")); object.__setattr__(self,"missing_value_policy",_enum(self.missing_value_policy,IndexValuePolicy,"missing_value_policy")); object.__setattr__(self,"multiple_value_policy",_enum(self.multiple_value_policy,IndexValuePolicy,"multiple_value_policy")); object.__setattr__(self,"status",_enum(self.status,IndexStatus,"status"))
        object.__setattr__(self,"normalization",text(self.normalization,"normalization")); object.__setattr__(self,"version",semantic_version(self.version)); object.__setattr__(self,"description",text(self.description,"description",optional=True)); object.__setattr__(self,"metadata",deep_freeze(self.metadata))
        if not isinstance(self.unique,bool) or not isinstance(self.case_sensitive,bool): raise IndexDefinitionError("definition flags must be boolean")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class IndexVersion(IndexModel):
    version: str
    revision: int=0
    parent_digest: str|None=None
    schema_version: str=INDEX_SCHEMA_VERSION
    discriminator: ClassVar[str]="index_version"
    def __post_init__(self)->None:
        object.__setattr__(self,"version",semantic_version(self.version)); object.__setattr__(self,"revision",non_negative(self.revision,"revision"))
        if self.parent_digest is not None and re.fullmatch(r"[0-9a-f]{64}",self.parent_digest) is None: raise IndexValidationError("parent_digest must be SHA-256")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class IndexEntry(IndexModel):
    key: IndexKey
    references: tuple[IndexReference,...]
    definition_id: IndexId
    version: IndexVersion
    status: IndexStatus
    created_at: datetime
    updated_at: datetime
    metadata: Mapping[str,object]=field(default_factory=dict)
    schema_version: str=INDEX_SCHEMA_VERSION
    discriminator: ClassVar[str]="index_entry"
    def __post_init__(self)->None:
        if not isinstance(self.key,IndexKey) or not isinstance(self.definition_id,IndexId) or not isinstance(self.version,IndexVersion): raise IndexValidationError("entry has invalid structural models")
        refs=tuple(self.references)
        if not refs or any(not isinstance(v,IndexReference) for v in refs): raise IndexValidationError("entry references must be non-empty")
        if len({v.sort_token for v in refs})!=len(refs): raise IndexValidationError("entry references must be unique")
        object.__setattr__(self,"references",tuple(sorted(refs,key=lambda v:v.sort_token))); object.__setattr__(self,"status",_enum(self.status,IndexStatus,"status"))
        object.__setattr__(self,"created_at",instant(self.created_at,"created_at")); object.__setattr__(self,"updated_at",instant(self.updated_at,"updated_at"))
        if self.updated_at < self.created_at: raise IndexValidationError("updated_at cannot precede created_at")
        object.__setattr__(self,"metadata",deep_freeze(self.metadata)); self._validate_schema()


@dataclass(frozen=True, slots=True)
class IndexStatistics(IndexModel):
    total_keys:int; total_entries:int; total_references:int; total_unique_references:int
    average_references_per_key:float; largest_cardinality:int; smallest_cardinality:int
    empty_key_count:int; logical_collision_count:int
    by_entity_type:Mapping[str,int]; by_namespace:Mapping[str,int]
    version:str; calculated_at:datetime
    schema_version:str=INDEX_SCHEMA_VERSION
    discriminator:ClassVar[str]="index_statistics"
    def __post_init__(self)->None:
        for name in ("total_keys","total_entries","total_references","total_unique_references","largest_cardinality","smallest_cardinality","empty_key_count","logical_collision_count"): object.__setattr__(self,name,non_negative(getattr(self,name),name))
        if not isinstance(self.average_references_per_key,(int,float)) or not math.isfinite(float(self.average_references_per_key)) or self.average_references_per_key<0: raise IndexValidationError("average must be finite and non-negative")
        object.__setattr__(self,"average_references_per_key",float(self.average_references_per_key)); object.__setattr__(self,"by_entity_type",deep_freeze(self.by_entity_type)); object.__setattr__(self,"by_namespace",deep_freeze(self.by_namespace)); object.__setattr__(self,"version",semantic_version(self.version)); object.__setattr__(self,"calculated_at",instant(self.calculated_at,"calculated_at")); self._validate_schema()


@dataclass(frozen=True, slots=True)
class IndexDescriptor(IndexModel):
    definition_id:IndexId; entry_count:int; reference_count:int; digest:str; consistency:IndexConsistency
    schema_version:str=INDEX_SCHEMA_VERSION
    discriminator:ClassVar[str]="index_descriptor"
    def __post_init__(self)->None:
        if not isinstance(self.definition_id,IndexId): raise IndexValidationError("definition_id must be IndexId")
        object.__setattr__(self,"entry_count",non_negative(self.entry_count,"entry_count")); object.__setattr__(self,"reference_count",non_negative(self.reference_count,"reference_count")); object.__setattr__(self,"consistency",_enum(self.consistency,IndexConsistency,"consistency"))
        if re.fullmatch(r"[0-9a-f]{64}",self.digest) is None: raise IndexValidationError("digest must be SHA-256")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class CanonicalIndex(IndexModel):
    identity:IndexIdentity; definition:IndexDefinition; metadata:IndexMetadata
    version:IndexVersion; entries:tuple[IndexEntry,...]; descriptor:IndexDescriptor
    schema_version:str=INDEX_SCHEMA_VERSION
    _factory_token:InitVar[object|None]=None
    discriminator:ClassVar[str]="canonical_index"
    def __post_init__(self,_factory_token:object|None)->None:
        if _factory_token is not _FACTORY_TOKEN: raise IndexFactoryError("CanonicalIndex must be created by IndexFactory")
        if not isinstance(self.identity,IndexIdentity) or not isinstance(self.definition,IndexDefinition) or not isinstance(self.metadata,IndexMetadata) or not isinstance(self.version,IndexVersion) or not isinstance(self.descriptor,IndexDescriptor): raise IndexValidationError("index has invalid structural models")
        entries=tuple(self.entries)
        if any(not isinstance(v,IndexEntry) for v in entries): raise IndexValidationError("entries must contain IndexEntry values")
        object.__setattr__(self,"entries",tuple(sorted(entries,key=lambda v:v.key.sort_token))); self._validate_schema()


@dataclass(frozen=True, slots=True)
class IndexCollection(IndexModel):
    indexes:tuple[CanonicalIndex,...]=(); name:str|None=None
    schema_version:str=INDEX_SCHEMA_VERSION
    _factory_token:InitVar[object|None]=None
    discriminator:ClassVar[str]="index_collection"
    def __post_init__(self,_factory_token:object|None)->None:
        if _factory_token is not _FACTORY_TOKEN: raise IndexFactoryError("IndexCollection must be created by IndexFactory")
        values=tuple(self.indexes)
        if any(not isinstance(v,CanonicalIndex) for v in values): raise IndexValidationError("indexes must contain CanonicalIndex values")
        if len({v.identity.canonical_id for v in values})!=len(values): raise IndexValidationError("collection index identities must be unique")
        object.__setattr__(self,"indexes",tuple(sorted(values,key=lambda v:str(v.identity.canonical_id)))); object.__setattr__(self,"name",text(self.name,"name",optional=True)); self._validate_schema()


@dataclass(frozen=True, slots=True)
class IndexOperation(IndexModel):
    operation_type:IndexOperationType; references:tuple[IndexReference,...]=(); keys:tuple[IndexKey,...]=(); timestamp:datetime|None=None
    schema_version:str=INDEX_SCHEMA_VERSION
    discriminator:ClassVar[str]="index_operation"
    def __post_init__(self)->None:
        object.__setattr__(self,"operation_type",_enum(self.operation_type,IndexOperationType,"operation_type")); object.__setattr__(self,"references",tuple(self.references)); object.__setattr__(self,"keys",tuple(self.keys))
        if any(not isinstance(v,IndexReference) for v in self.references) or any(not isinstance(v,IndexKey) for v in self.keys): raise IndexValidationError("operation contains invalid values")
        if self.timestamp is not None: object.__setattr__(self,"timestamp",instant(self.timestamp,"timestamp"))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class IndexOperationResult(IndexModel):
    operation:IndexOperationType; previous_version:IndexVersion; resulting_version:IndexVersion
    affected_entries:int; warnings:tuple[str,...]; digest:str; timestamp:datetime
    schema_version:str=INDEX_SCHEMA_VERSION
    discriminator:ClassVar[str]="index_operation_result"
    def __post_init__(self)->None:
        object.__setattr__(self,"operation",_enum(self.operation,IndexOperationType,"operation")); object.__setattr__(self,"affected_entries",non_negative(self.affected_entries,"affected_entries")); object.__setattr__(self,"warnings",tuple(text(v,"warning") for v in self.warnings)); object.__setattr__(self,"timestamp",instant(self.timestamp,"timestamp"))
        if not isinstance(self.previous_version,IndexVersion) or not isinstance(self.resulting_version,IndexVersion): raise IndexValidationError("operation versions must be IndexVersion")
        if re.fullmatch(r"[0-9a-f]{64}",self.digest) is None: raise IndexValidationError("digest must be SHA-256")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class IndexQuery(IndexModel):
    exact_key:IndexKey|None=None; exact_keys:tuple[IndexKey,...]=(); text_prefix:str|None=None
    lower_bound:IndexKey|None=None; upper_bound:IndexKey|None=None; reference_type:IndexTarget|None=None
    version:str|None=None; namespace:str|None=None; limit:int=100; offset:int=0
    schema_version:str=INDEX_SCHEMA_VERSION
    discriminator:ClassVar[str]="index_query"
    def __post_init__(self)->None:
        keys=tuple(self.exact_keys)
        if self.exact_key is not None and not isinstance(self.exact_key,IndexKey): raise IndexQueryError("exact_key must be IndexKey")
        if any(not isinstance(v,IndexKey) for v in keys): raise IndexQueryError("exact_keys must contain IndexKey values")
        if self.exact_key is not None and keys: raise IndexQueryError("exact_key and exact_keys are mutually exclusive")
        object.__setattr__(self,"exact_keys",keys); object.__setattr__(self,"text_prefix",text(self.text_prefix,"text_prefix",optional=True)); object.__setattr__(self,"namespace",text(self.namespace,"namespace",optional=True))
        if self.reference_type is not None: object.__setattr__(self,"reference_type",_enum(self.reference_type,IndexTarget,"reference_type"))
        if self.version is not None: object.__setattr__(self,"version",semantic_version(self.version))
        if (self.lower_bound is None)!=(self.upper_bound is None): raise IndexQueryError("range requires lower and upper bounds")
        if self.lower_bound is not None and self.lower_bound.key_type != self.upper_bound.key_type: raise IndexQueryError("range boundaries must have the same key type")
        object.__setattr__(self,"limit",non_negative(self.limit,"limit")); object.__setattr__(self,"offset",non_negative(self.offset,"offset"))
        if self.limit==0: raise IndexQueryError("limit must be greater than zero")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class IndexResult(IndexModel):
    references:tuple[IndexReference,...]; matched_keys:tuple[IndexKey,...]; total:int; limit:int; offset:int; index_digest:str; metadata:Mapping[str,object]=field(default_factory=dict)
    schema_version:str=INDEX_SCHEMA_VERSION
    discriminator:ClassVar[str]="index_result"
    def __post_init__(self)->None:
        object.__setattr__(self,"references",tuple(self.references)); object.__setattr__(self,"matched_keys",tuple(self.matched_keys)); object.__setattr__(self,"total",non_negative(self.total,"total")); object.__setattr__(self,"limit",non_negative(self.limit,"limit")); object.__setattr__(self,"offset",non_negative(self.offset,"offset")); object.__setattr__(self,"metadata",deep_freeze(self.metadata))
        if re.fullmatch(r"[0-9a-f]{64}",self.index_digest) is None: raise IndexValidationError("index_digest must be SHA-256")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class IndexSnapshot(IndexModel):
    snapshot_id:IndexId; index_id:IndexId; version:IndexVersion; definition:IndexDefinition
    digest:str; entry_count:int; statistics:IndexStatistics; created_at:datetime; snapshot_type:IndexSnapshotType
    schema_version:str=INDEX_SCHEMA_VERSION
    _factory_token:InitVar[object|None]=None
    discriminator:ClassVar[str]="index_snapshot"
    def __post_init__(self,_factory_token:object|None)->None:
        if _factory_token is not _FACTORY_TOKEN: raise IndexFactoryError("IndexSnapshot must be created by IndexFactory")
        if not isinstance(self.snapshot_id,IndexId) or not isinstance(self.index_id,IndexId) or not isinstance(self.version,IndexVersion) or not isinstance(self.definition,IndexDefinition) or not isinstance(self.statistics,IndexStatistics): raise IndexValidationError("snapshot has invalid structural models")
        if re.fullmatch(r"[0-9a-f]{64}",self.digest) is None: raise IndexValidationError("digest must be SHA-256")
        object.__setattr__(self,"entry_count",non_negative(self.entry_count,"entry_count")); object.__setattr__(self,"created_at",instant(self.created_at,"created_at")); object.__setattr__(self,"snapshot_type",_enum(self.snapshot_type,IndexSnapshotType,"snapshot_type")); self._validate_schema()


__all__=["CanonicalIndex","IndexCollection","IndexDefinition","IndexDescriptor","IndexEntry","IndexField","IndexKey","IndexOperation","IndexOperationResult","IndexQuery","IndexReference","IndexResult","IndexSnapshot","IndexStatistics","IndexVersion"]
