"""Closed-schema deterministic UTF-8 JSON serializer for index models."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from decimal import Decimal
from typing import Mapping
from uuid import UUID

from .contracts import INDEX_SCHEMA_VERSION, IndexModel
from .enums import *
from .errors import IndexSerializationError
from .factory import IndexFactory
from .identity import IndexId, IndexIdentity
from .metadata import IndexMetadata
from .models import *

_MODELS={c.discriminator for c in (IndexId,IndexIdentity,IndexMetadata,IndexKey,IndexReference,IndexEntry,IndexField,IndexDefinition,IndexVersion,IndexStatistics,IndexSnapshot,IndexDescriptor,CanonicalIndex,IndexCollection,IndexOperation,IndexOperationResult,IndexQuery,IndexResult)}


def _strict(value:object,model:str,names:set[str])->Mapping[str,object]:
    if not isinstance(value,Mapping) or set(value)!=(names|{"model","schema_version"}): raise IndexSerializationError(f"invalid or unknown {model} fields")
    if value.get("model")!=model: raise IndexSerializationError(f"invalid {model} discriminator")
    if value.get("schema_version")!=INDEX_SCHEMA_VERSION: raise IndexSerializationError(f"unsupported {model} schema_version")
    return value


def _dt(value:object)->datetime:
    try:return datetime.fromisoformat(str(value))
    except (TypeError,ValueError) as error:raise IndexSerializationError("invalid UTC datetime") from error


def _map(value:object)->Mapping[str,object]:
    if not isinstance(value,Mapping):raise IndexSerializationError("expected object")
    return value


def _list(value:object)->list:
    if not isinstance(value,list):raise IndexSerializationError("expected array")
    return value


class DeterministicIndexSerializer:
    def __init__(self,factory:IndexFactory|None=None)->None:self._factory=factory or IndexFactory()
    def serialize(self,value:IndexModel)->bytes:
        if not isinstance(value,IndexModel) or value.model not in _MODELS:raise IndexSerializationError("unknown index model")
        try:return json.dumps(value.to_dict(),ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(",",":")).encode("utf-8")
        except (TypeError,ValueError) as error:raise IndexSerializationError("index model is not serializable") from error
    def digest(self,value:IndexModel)->str:return hashlib.sha256(self.serialize(value)).hexdigest()
    def deserialize(self,payload:bytes|str)->IndexModel:
        if isinstance(payload,bytes):
            try:raw=payload.decode("utf-8")
            except UnicodeDecodeError as error:raise IndexSerializationError("payload must be UTF-8") from error
        elif isinstance(payload,str):raw=payload
        else:raise IndexSerializationError("payload must be bytes or string")
        try:value=json.loads(raw,parse_constant=lambda token:(_ for _ in ()).throw(ValueError(token)))
        except (json.JSONDecodeError,ValueError) as error:raise IndexSerializationError("payload must be valid canonical JSON") from error
        canonical=json.dumps(value,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(",",":"))
        if raw!=canonical:raise IndexSerializationError("payload is not canonical JSON")
        return self._decode(value)
    def _value(self,value:object)->object:
        if isinstance(value,Mapping):
            if set(value)=={"__index_scalar__","value"} and value["__index_scalar__"]=="decimal":return Decimal(str(value["value"]))
            if "model" in value:return self._decode(value)
            return {str(k):self._value(v) for k,v in value.items()}
        if isinstance(value,list):return tuple(self._value(v) for v in value)
        return value
    def _decode(self,payload:object)->IndexModel:
        if not isinstance(payload,Mapping) or not isinstance(payload.get("model"),str):raise IndexSerializationError("model discriminator is required")
        m=payload["model"]
        if m not in _MODELS:raise IndexSerializationError(f"unknown model discriminator: {m}")
        n=lambda v:self._decode(v)
        if m=="index_id":
            v=_strict(payload,m,{"value"});return IndexId(UUID(str(v["value"])))
        if m=="index_identity":
            v=_strict(payload,m,{"logical_id","canonical_id","definition_id","namespace","name","version"});return IndexIdentity(n(v["logical_id"]),n(v["canonical_id"]),n(v["definition_id"]),v["namespace"],v["name"],v["version"]) # type: ignore[arg-type]
        if m=="index_metadata":
            v=_strict(payload,m,{"created_at","updated_at","created_by","status","attributes"});return IndexMetadata(_dt(v["created_at"]),_dt(v["updated_at"]),v["created_by"],IndexStatus(v["status"]),self._value(_map(v["attributes"]))) # type: ignore[arg-type]
        if m=="index_key":
            v=_strict(payload,m,{"value","key_type"});kt=IndexKeyType(v["key_type"])
            value=(tuple(n(x).value for x in _list(v["value"]))
                   if kt is IndexKeyType.SEQUENCE else self._value(v["value"]))
            if kt is IndexKeyType.UUID:value=UUID(str(value))
            elif kt is IndexKeyType.DATETIME:value=_dt(value)
            return IndexKey(value,kt)
        if m=="index_reference":
            v=_strict(payload,m,{"namespace","canonical_id","entity_type","version","entity_discriminator","checksum","metadata"});return IndexReference(v["namespace"],v["canonical_id"],IndexTarget(v["entity_type"]),v["version"],v["entity_discriminator"],v["checksum"],self._value(_map(v["metadata"]))) # type: ignore[arg-type]
        if m=="index_field":
            v=_strict(payload,m,{"path","key_type","required"});return IndexField(v["path"],None if v["key_type"] is None else IndexKeyType(v["key_type"]),v["required"]) # type: ignore[arg-type]
        if m=="index_definition":
            v=_strict(payload,m,{"definition_id","name","namespace","index_type","targets","fields","unique","multiplicity","normalization","case_sensitive","missing_value_policy","multiple_value_policy","status","version","description","metadata"})
            result=self._factory.create_definition(name=v["name"],namespace=v["namespace"],index_type=IndexType(v["index_type"]),targets=tuple(IndexTarget(x) for x in _list(v["targets"])),fields=tuple(n(x) for x in _list(v["fields"])),unique=v["unique"],multiplicity=IndexMultiplicity(v["multiplicity"]),normalization=v["normalization"],case_sensitive=v["case_sensitive"],missing_value_policy=IndexValuePolicy(v["missing_value_policy"]),multiple_value_policy=IndexValuePolicy(v["multiple_value_policy"]),status=IndexStatus(v["status"]),version=v["version"],description=v["description"],metadata=self._value(_map(v["metadata"]))) # type: ignore[arg-type]
            if result.definition_id!=n(v["definition_id"]):raise IndexSerializationError("definition identity is inconsistent")
            return result
        if m=="index_version":
            v=_strict(payload,m,{"version","revision","parent_digest"});return IndexVersion(v["version"],v["revision"],v["parent_digest"]) # type: ignore[arg-type]
        if m=="index_entry":
            v=_strict(payload,m,{"key","references","definition_id","version","status","created_at","updated_at","metadata"});return IndexEntry(n(v["key"]),tuple(n(x) for x in _list(v["references"])),n(v["definition_id"]),n(v["version"]),IndexStatus(v["status"]),_dt(v["created_at"]),_dt(v["updated_at"]),self._value(_map(v["metadata"]))) # type: ignore[arg-type]
        if m=="index_statistics":
            names={"total_keys","total_entries","total_references","total_unique_references","average_references_per_key","largest_cardinality","smallest_cardinality","empty_key_count","logical_collision_count","by_entity_type","by_namespace","version","calculated_at"};v=_strict(payload,m,names);return IndexStatistics(*(v[x] for x in list(names)[:0])) if False else IndexStatistics(v["total_keys"],v["total_entries"],v["total_references"],v["total_unique_references"],v["average_references_per_key"],v["largest_cardinality"],v["smallest_cardinality"],v["empty_key_count"],v["logical_collision_count"],self._value(_map(v["by_entity_type"])),self._value(_map(v["by_namespace"])),v["version"],_dt(v["calculated_at"])) # type: ignore[arg-type]
        if m=="index_descriptor":
            v=_strict(payload,m,{"definition_id","entry_count","reference_count","digest","consistency"});return IndexDescriptor(n(v["definition_id"]),v["entry_count"],v["reference_count"],v["digest"],IndexConsistency(v["consistency"])) # type: ignore[arg-type]
        if m=="canonical_index":
            v=_strict(payload,m,{"identity","definition","metadata","version","entries","descriptor"});return self._factory.from_parts(identity=n(v["identity"]),definition=n(v["definition"]),metadata=n(v["metadata"]),version=n(v["version"]),entries=tuple(n(x) for x in _list(v["entries"])),descriptor=n(v["descriptor"])) # type: ignore[arg-type]
        if m=="index_collection":
            v=_strict(payload,m,{"indexes","name"});return self._factory.create_collection(tuple(n(x) for x in _list(v["indexes"])),v["name"]) # type: ignore[arg-type]
        if m=="index_operation":
            v=_strict(payload,m,{"operation_type","references","keys","timestamp"});return IndexOperation(IndexOperationType(v["operation_type"]),tuple(n(x) for x in _list(v["references"])),tuple(n(x) for x in _list(v["keys"])),None if v["timestamp"] is None else _dt(v["timestamp"]))
        if m=="index_operation_result":
            v=_strict(payload,m,{"operation","previous_version","resulting_version","affected_entries","warnings","digest","timestamp"});return IndexOperationResult(IndexOperationType(v["operation"]),n(v["previous_version"]),n(v["resulting_version"]),v["affected_entries"],tuple(_list(v["warnings"])),v["digest"],_dt(v["timestamp"])) # type: ignore[arg-type]
        if m=="index_query":
            v=_strict(payload,m,{"exact_key","exact_keys","text_prefix","lower_bound","upper_bound","reference_type","version","namespace","limit","offset"});return IndexQuery(None if v["exact_key"] is None else n(v["exact_key"]),tuple(n(x) for x in _list(v["exact_keys"])),v["text_prefix"],None if v["lower_bound"] is None else n(v["lower_bound"]),None if v["upper_bound"] is None else n(v["upper_bound"]),None if v["reference_type"] is None else IndexTarget(v["reference_type"]),v["version"],v["namespace"],v["limit"],v["offset"]) # type: ignore[arg-type]
        if m=="index_result":
            v=_strict(payload,m,{"references","matched_keys","total","limit","offset","index_digest","metadata"});return IndexResult(tuple(n(x) for x in _list(v["references"])),tuple(n(x) for x in _list(v["matched_keys"])),v["total"],v["limit"],v["offset"],v["index_digest"],self._value(_map(v["metadata"]))) # type: ignore[arg-type]
        if m=="index_snapshot":
            v=_strict(payload,m,{"snapshot_id","index_id","version","definition","digest","entry_count","statistics","created_at","snapshot_type"});return self._factory.snapshot_from_parts(snapshot_id=n(v["snapshot_id"]),index_id=n(v["index_id"]),version=n(v["version"]),definition=n(v["definition"]),digest=v["digest"],entry_count=v["entry_count"],statistics=n(v["statistics"]),created_at=_dt(v["created_at"]),snapshot_type=IndexSnapshotType(v["snapshot_type"])) # type: ignore[arg-type]
        raise IndexSerializationError("unknown model")


__all__=["DeterministicIndexSerializer"]
