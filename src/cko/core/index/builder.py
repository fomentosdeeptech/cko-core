"""Transient builder for immutable canonical indexes."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from enum import Enum
from typing import Callable, Mapping

from cko.core.documents import CanonicalDocument
from cko.core.graph import CanonicalGraph
from cko.core.knowledge import KnowledgeObject
from cko.core.query import CanonicalQuery
from cko.core.relationships import CanonicalRelationship

from .enums import IndexMultiplicity, IndexOperationType, IndexStatus, IndexTarget, IndexValuePolicy
from .errors import IndexOperationError, IndexValidationError
from .factory import IndexFactory
from .models import (CanonicalIndex, IndexDefinition, IndexEntry, IndexKey,
                     IndexOperationResult, IndexReference, IndexVersion)

_TARGETS={KnowledgeObject:IndexTarget.KNOWLEDGE_OBJECT,CanonicalDocument:IndexTarget.CANONICAL_DOCUMENT,
          CanonicalRelationship:IndexTarget.CANONICAL_RELATIONSHIP,CanonicalGraph:IndexTarget.CANONICAL_GRAPH,
          CanonicalQuery:IndexTarget.CANONICAL_QUERY}


def _pick(value:object,name:str)->object|None:
    if isinstance(value,Mapping): return value.get(name)
    return getattr(value,name,None)


def _resolve(entity:object,path:str)->object|None:
    root,_,tail=path.partition(".")
    identity=getattr(entity,"identity",None); metadata=getattr(entity,"metadata",None); descriptor=getattr(entity,"descriptor",None)
    aliases={
        "identity":getattr(identity,"canonical_id",None) or getattr(identity,"document_id",None),
        "namespace":getattr(identity,"namespace",None),
        "type":getattr(identity,"knowledge_type",None) or getattr(descriptor,"document_type",None) or getattr(descriptor,"relationship_type",None),
        "entity_type":next((target.value for cls,target in _TARGETS.items() if isinstance(entity,cls)),None),
        "document_type":getattr(descriptor,"document_type",None),
        "relationship_type":getattr(descriptor,"relationship_type",None),
        "status":getattr(metadata,"status",None) or getattr(descriptor,"status",None),
        "creator":getattr(metadata,"creator",None) or getattr(metadata,"created_by",None),
        "created_at":getattr(metadata,"created_at",None),
        "updated_at":getattr(metadata,"modified_at",None) or getattr(metadata,"updated_at",None),
        "version":getattr(identity,"version",None) or getattr(metadata,"version",None),
        "checksum":getattr(metadata,"checksum",None),
    }
    if root in aliases and aliases[root] is not None:
        current=aliases[root]
        if not tail:return current
        for part in tail.split("."):
            current=_pick(current,part)
            if current is None:return None
        return current
    current=entity
    for part in path.split("."):
        found=_pick(current,part)
        if found is None and current is entity:
            for container in ("identity","metadata","descriptor","content","version","integrity"):
                nested=_pick(entity,container)
                found=_pick(nested,part) if nested is not None else None
                if found is not None: break
        current=found
        if current is None: return None
    return current


def _key_value(value:object)->object:
    if isinstance(value,Enum):return value.value
    candidate=getattr(value,"value",None)
    if candidate is not None and isinstance(candidate,(str,int,bool)):return candidate
    if hasattr(value,"name") and isinstance(getattr(value,"name"),str):return getattr(value,"name")
    if hasattr(value,"identifier") and isinstance(getattr(value,"identifier"),str):return getattr(value,"identifier")
    return value


def reference_from_entity(entity:object)->IndexReference:
    target=next((target for cls,target in _TARGETS.items() if isinstance(entity,cls)),None)
    if target is None: raise IndexValidationError("unsupported canonical index target")
    identity=getattr(entity,"identity",None)
    namespace=getattr(identity,"namespace",None)
    identifier=getattr(identity,"canonical_id",None) or getattr(identity,"document_id",None)
    version=getattr(identity,"version",None)
    if version is None:
        candidate=getattr(entity,"version",None) or getattr(getattr(entity,"metadata",None),"version",None)
        version=getattr(candidate,"version",candidate)
    version=version or "1.0.0"
    checksum=getattr(getattr(entity,"metadata",None),"checksum",None)
    checksum=getattr(checksum,"value",checksum)
    if not isinstance(checksum,str) or re.fullmatch(r"[0-9a-fA-F]{64}",checksum) is None: checksum=None
    return IndexReference(str(namespace),str(identifier),target,str(version),getattr(entity,"model",type(entity).__name__),checksum)


class IndexBuilder:
    def __init__(self, definition:IndexDefinition, *, factory:IndexFactory|None=None,
                 clock:Callable[[],datetime]|None=None, created_by:str="cko.core.index") -> None:
        if not isinstance(definition,IndexDefinition): raise IndexValidationError("definition must be IndexDefinition")
        self.definition=definition; self._clock=clock or (lambda:datetime.now(UTC)); self._factory=factory or IndexFactory(clock=self._clock)
        self._created_by=created_by; self._entries:dict[str,tuple[IndexKey,list[IndexReference],datetime]]={}; self._base:CanonicalIndex|None=None
        self.last_result:IndexOperationResult|None=None

    @classmethod
    def from_index(cls,index:CanonicalIndex,**kwargs)->"IndexBuilder":
        result=cls(index.definition,**kwargs); result._base=index
        for entry in index.entries: result._entries[entry.key.sort_token]=(entry.key,list(entry.references),entry.created_at)
        return result

    def add(self,entity:object, key:object|None=None)->"IndexBuilder":
        reference=entity if isinstance(entity,IndexReference) else reference_from_entity(entity)
        if reference.entity_type not in self.definition.targets: raise IndexValidationError("reference target is incompatible with index definition")
        values=self._keys(entity,key)
        for selected in values:
            token=selected.sort_token; now=self._clock(); current=self._entries.get(token)
            refs=[] if current is None else current[1]
            if reference in refs: raise IndexOperationError("reference is already indexed for key")
            if self.definition.unique and refs: raise IndexOperationError("unique index key already has a reference")
            self._entries[token]=(selected,[*refs,reference],current[2] if current else now)
        return self

    def add_reference(self,key:object,reference:IndexReference)->"IndexBuilder": return self.add(reference,key)

    def remove(self,entity_or_reference:object,key:object|None=None)->"IndexBuilder":
        reference=entity_or_reference if isinstance(entity_or_reference,IndexReference) else reference_from_entity(entity_or_reference)
        keys=list(self._entries.values()) if key is None else [self._entries.get(IndexKey(key).sort_token)]
        changed=False
        for current in keys:
            if current is None: continue
            selected,refs,created=current
            remaining=[v for v in refs if v.sort_token!=reference.sort_token]
            if len(remaining)!=len(refs):
                changed=True
                if remaining:self._entries[selected.sort_token]=(selected,remaining,created)
                else:self._entries.pop(selected.sort_token,None)
        if not changed: raise IndexOperationError("remove operation had no effect")
        return self

    def remove_reference(self,key:object,reference:IndexReference)->"IndexBuilder": return self.remove(reference,key)

    def replace(self,old:object,new:object,key:object|None=None)->"IndexBuilder":
        self.remove(old,key); self.add(new,key); return self

    def clear(self)->"IndexBuilder": self._entries.clear(); return self

    def rebuild(self,entities:tuple[object,...])->"IndexBuilder":
        self._entries.clear()
        for entity in entities:self.add(entity)
        return self

    def merge(self,index:CanonicalIndex)->"IndexBuilder":
        if index.definition.definition_id!=self.definition.definition_id: raise IndexOperationError("cannot merge incompatible index definitions")
        for entry in index.entries:
            for reference in entry.references:self.add_reference(entry.key.value,reference)
        return self

    def build(self,entities:tuple[object,...]|None=None)->CanonicalIndex:
        if entities is not None:
            self._entries.clear()
            for entity in entities:self.add(entity)
        now=self._clock(); base=self._base; revision=(base.version.revision+1 if base else 0); parent=(base.descriptor.digest if base else None)
        version=IndexVersion(self.definition.version,revision,parent)
        entries=tuple(IndexEntry(key,tuple(refs),self.definition.definition_id,version,IndexStatus.ACTIVE,created,now)
                      for key,refs,created in self._entries.values())
        result=self._factory.create_index(self.definition,name=(base.identity.name if base else None),created_by=self._created_by,
            entries=entries,logical_id=(base.identity.logical_id if base else None),revision=revision,parent_digest=parent,
            created_at=(base.metadata.created_at if base else now),updated_at=now)
        return result

    def snapshot(self,snapshot_type=None):
        from .enums import IndexSnapshotType
        return self._factory.create_snapshot(self.build(),snapshot_type or IndexSnapshotType.FULL)

    def statistics(self):
        from .statistics import DefaultIndexStatisticsProvider
        return DefaultIndexStatisticsProvider(self._clock).calculate(self.build())

    def _keys(self,entity:object,explicit:object|None)->tuple[IndexKey,...]:
        if explicit is not None:return (explicit if isinstance(explicit,IndexKey) else IndexKey(explicit),)
        values=[]
        for field in self.definition.fields:
            value=_resolve(entity,field.path)
            if value is None:
                if field.required and self.definition.missing_value_policy is IndexValuePolicy.REJECT: raise IndexValidationError(f"missing indexed field: {field.path}")
                if self.definition.missing_value_policy is IndexValuePolicy.IGNORE:return ()
            values.append(_key_value(value))
        if len(values)==1 and isinstance(values[0],(tuple,list)) and self.definition.multiplicity is IndexMultiplicity.MULTIPLE:
            return tuple(IndexKey(_key_value(v)) for v in values[0])
        value=values[0] if len(values)==1 else tuple(values)
        if not self.definition.case_sensitive and isinstance(value,str):value=value.casefold()
        return (IndexKey(value),)


__all__=["IndexBuilder","reference_from_entity"]
