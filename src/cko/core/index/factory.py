"""Mandatory construction boundary for canonical index aggregates."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Callable, Mapping

from .contracts import INDEX_VERSION, primitive
from .enums import (IndexConsistency, IndexMultiplicity, IndexSnapshotType,
                    IndexStatus, IndexTarget, IndexType, IndexValuePolicy)
from .errors import IndexFactoryError
from .identity import IndexId, IndexIdentity
from .metadata import IndexMetadata
from .models import (_FACTORY_TOKEN, CanonicalIndex, IndexCollection,
                     IndexDefinition, IndexDescriptor, IndexEntry, IndexField,
                     IndexSnapshot, IndexVersion)


def canonical_digest(value: object) -> str:
    data=json.dumps(primitive(value),ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


class IndexFactory:
    def __init__(self, validator=None, clock:Callable[[],datetime]|None=None)->None:
        from .validator import IndexValidator
        self._validator=validator or IndexValidator(); self._clock=clock or (lambda:datetime.now(UTC))

    def create_definition(self, *, name:str, namespace:str, index_type:IndexType,
                          targets:tuple[IndexTarget,...], fields:tuple[IndexField,...],
                          unique:bool=False, multiplicity:IndexMultiplicity=IndexMultiplicity.SINGLE,
                          normalization:str="canonical", case_sensitive:bool=True,
                          missing_value_policy:IndexValuePolicy=IndexValuePolicy.REJECT,
                          multiple_value_policy:IndexValuePolicy=IndexValuePolicy.REJECT,
                          status:IndexStatus=IndexStatus.ACTIVE, version:str=INDEX_VERSION,
                          description:str|None=None, metadata:Mapping[str,object]|None=None)->IndexDefinition:
        structural={"name":name.strip(),"namespace":namespace.strip(),"index_type":IndexType(index_type).value,
                    "targets":sorted(IndexTarget(v).value for v in targets),"fields":sorted(v.path for v in fields),
                    "unique":unique,"multiplicity":IndexMultiplicity(multiplicity).value,"normalization":normalization,
                    "case_sensitive":case_sensitive,"missing":IndexValuePolicy(missing_value_policy).value,
                    "multiple":IndexValuePolicy(multiple_value_policy).value,"version":version}
        key=json.dumps(structural,ensure_ascii=False,sort_keys=True,separators=(",",":"))
        result=IndexDefinition(IndexId.canonical(namespace,key),name,namespace,index_type,targets,fields,unique,multiplicity,
                               normalization,case_sensitive,missing_value_policy,multiple_value_policy,status,version,
                               description,metadata or {},_factory_token=_FACTORY_TOKEN)
        self._validator.validate(result); return result

    def create_index(self, definition:IndexDefinition, *, name:str|None=None, created_by:str="cko.core.index",
                     entries:tuple[IndexEntry,...]=(), logical_id:IndexId|None=None,
                     version:str|None=None, revision:int=0, parent_digest:str|None=None,
                     created_at:datetime|None=None, updated_at:datetime|None=None,
                     metadata:Mapping[str,object]|None=None)->CanonicalIndex:
        if not isinstance(definition,IndexDefinition): raise IndexFactoryError("definition must be IndexDefinition")
        now=created_at or self._clock(); modified=updated_at or now; selected_version=version or definition.version
        logical=logical_id or IndexId.new(); canonical=IndexId.canonical(definition.namespace,f"{logical}:{definition.definition_id}:{selected_version}")
        identity=IndexIdentity(logical,canonical,definition.definition_id,definition.namespace,name or definition.name,selected_version)
        index_version=IndexVersion(selected_version,revision,parent_digest)
        prepared=tuple(entries)
        digest=self.entries_digest(definition,index_version,prepared)
        descriptor=IndexDescriptor(definition.definition_id,len(prepared),sum(len(v.references) for v in prepared),digest,IndexConsistency.CONSISTENT)
        result=CanonicalIndex(identity,definition,IndexMetadata(now,modified,created_by,IndexStatus.ACTIVE,metadata or {}),index_version,prepared,descriptor,_factory_token=_FACTORY_TOKEN)
        self._validator.validate(result); return result

    @staticmethod
    def entries_digest(definition:IndexDefinition, version:IndexVersion, entries:tuple[IndexEntry,...])->str:
        return canonical_digest({"definition_id":str(definition.definition_id),"version":version.to_dict(),"entries":[v.to_dict() for v in sorted(entries,key=lambda e:e.key.sort_token)]})

    def from_parts(self, *, identity:IndexIdentity, definition:IndexDefinition, metadata:IndexMetadata,
                   version:IndexVersion, entries:tuple[IndexEntry,...], descriptor:IndexDescriptor)->CanonicalIndex:
        result=CanonicalIndex(identity,definition,metadata,version,entries,descriptor,_factory_token=_FACTORY_TOKEN); self._validator.validate(result); return result

    def create_collection(self,indexes:tuple[CanonicalIndex,...]=(),name:str|None=None)->IndexCollection:
        result=IndexCollection(indexes,name,_factory_token=_FACTORY_TOKEN); self._validator.validate(result); return result

    def create_snapshot(self,index:CanonicalIndex,snapshot_type:IndexSnapshotType=IndexSnapshotType.FULL)->IndexSnapshot:
        from .statistics import DefaultIndexStatisticsProvider
        stats=DefaultIndexStatisticsProvider(self._clock).calculate(index)
        sid=IndexId.canonical(index.definition.namespace,f"snapshot:{index.identity.canonical_id}:{index.descriptor.digest}:{snapshot_type.value}")
        result=IndexSnapshot(sid,index.identity.canonical_id,index.version,index.definition,index.descriptor.digest,len(index.entries),stats,self._clock(),snapshot_type,_factory_token=_FACTORY_TOKEN)
        self._validator.validate(result,index=index); return result

    def snapshot_from_parts(self, *, snapshot_id:IndexId,index_id:IndexId,version:IndexVersion,
                            definition:IndexDefinition,digest:str,entry_count:int,statistics,
                            created_at:datetime,snapshot_type:IndexSnapshotType)->IndexSnapshot:
        return IndexSnapshot(snapshot_id,index_id,version,definition,digest,entry_count,statistics,created_at,snapshot_type,_factory_token=_FACTORY_TOKEN)


__all__=["IndexFactory","canonical_digest"]
