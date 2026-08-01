"""Structural and cross-model validation for canonical indexes."""

from __future__ import annotations

from dataclasses import is_dataclass

from .contracts import IndexModel
from .errors import IndexConsistencyError, IndexValidationError
from .models import (CanonicalIndex, IndexCollection, IndexDefinition,
                     IndexEntry, IndexQuery, IndexSnapshot)


class IndexValidator:
    def validate(self,value:IndexModel,*,index:CanonicalIndex|None=None)->None:
        if not isinstance(value,IndexModel) or not is_dataclass(value): raise IndexValidationError("value must be a canonical index dataclass")
        value._validate_schema(); params=getattr(type(value),"__dataclass_params__",None)
        if params is None or not params.frozen or not hasattr(type(value),"__slots__"): raise IndexValidationError("index models must be frozen and slotted")
        if value.model!=type(value).discriminator: raise IndexValidationError("invalid model discriminator")
        if isinstance(value,CanonicalIndex):self._index(value)
        elif isinstance(value,IndexDefinition):self._definition(value)
        elif isinstance(value,IndexEntry):self._entry(value,None)
        elif isinstance(value,IndexCollection):
            definitions={}
            for item in value.indexes:
                self._index(item); key=(item.definition.namespace,item.definition.name)
                if key in definitions and definitions[key]!=item.definition.definition_id: raise IndexConsistencyError("collection contains conflicting definitions")
                definitions[key]=item.definition.definition_id
        elif isinstance(value,IndexSnapshot) and index is not None:
            if value.index_id!=index.identity.canonical_id or value.digest!=index.descriptor.digest or value.entry_count!=len(index.entries): raise IndexConsistencyError("snapshot digest or origin is inconsistent")
        elif isinstance(value,IndexQuery): pass

    def _definition(self,value:IndexDefinition)->None:
        if value.unique and value.multiplicity.value=="multiple": raise IndexConsistencyError("unique definitions cannot declare multiple multiplicity")

    def _entry(self,value:IndexEntry,definition:IndexDefinition|None)->None:
        if definition is None:return
        if value.definition_id!=definition.definition_id: raise IndexConsistencyError("entry definition is inconsistent")
        if any(ref.entity_type not in definition.targets for ref in value.references): raise IndexConsistencyError("entry reference target is incompatible")
        if definition.unique and len(value.references)>1: raise IndexConsistencyError("unique index has multiple references for a key")

    def _index(self,value:CanonicalIndex)->None:
        from .factory import IndexFactory
        self._definition(value.definition)
        if value.identity.definition_id!=value.definition.definition_id or value.descriptor.definition_id!=value.definition.definition_id: raise IndexConsistencyError("index definition identities are inconsistent")
        tokens=[entry.key.sort_token for entry in value.entries]
        if len(tokens)!=len(set(tokens)): raise IndexConsistencyError("index contains duplicate keys")
        for entry in value.entries:self._entry(entry,value.definition)
        if value.descriptor.entry_count!=len(value.entries) or value.descriptor.reference_count!=sum(len(v.references) for v in value.entries): raise IndexConsistencyError("index descriptor counts are inconsistent")
        expected=IndexFactory.entries_digest(value.definition,value.version,value.entries)
        if value.descriptor.digest!=expected: raise IndexConsistencyError("index digest is invalid or content was altered")


__all__=["IndexValidator"]
