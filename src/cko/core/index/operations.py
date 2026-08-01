"""Deterministic structural operations and reads over canonical indexes."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable

from .builder import IndexBuilder
from .enums import IndexOperationType, IndexOrdering
from .errors import IndexOperationError, IndexQueryError
from .models import (CanonicalIndex, IndexOperation, IndexOperationResult,
                     IndexQuery, IndexResult)


class InMemoryIndexOperations:
    def __init__(self,clock:Callable[[],datetime]|None=None)->None:self._clock=clock or (lambda:datetime.now(UTC))

    def execute(self,index:CanonicalIndex,operation:IndexOperation,*,merge_index:CanonicalIndex|None=None)->tuple[CanonicalIndex,IndexOperationResult]:
        builder=IndexBuilder.from_index(index,clock=self._clock); before=len(index.entries); kind=operation.operation_type
        if kind is IndexOperationType.CLEAR: builder.clear()
        elif kind is IndexOperationType.MERGE:
            if merge_index is None: raise IndexOperationError("merge operation requires merge_index")
            builder.merge(merge_index)
        elif kind is IndexOperationType.REBUILD:
            if len(operation.references)!=len(operation.keys): raise IndexOperationError("structural rebuild requires one key per reference")
            builder.clear()
            for key,reference in zip(operation.keys,operation.references):builder.add_reference(key.value,reference)
        elif kind in {IndexOperationType.ADD,IndexOperationType.REMOVE}:
            if not operation.references or not operation.keys: raise IndexOperationError("add/remove requires references and keys")
            for key in operation.keys:
                for reference in operation.references:
                    (builder.add_reference if kind is IndexOperationType.ADD else builder.remove_reference)(key.value,reference)
        elif kind is IndexOperationType.REPLACE:
            if len(operation.references)!=2 or len(operation.keys)!=1: raise IndexOperationError("replace requires old/new references and one key")
            builder.replace(operation.references[0],operation.references[1],operation.keys[0].value)
        result=builder.build()
        old={v.key.sort_token:v.references for v in index.entries}; new={v.key.sort_token:v.references for v in result.entries}
        affected=sum(old.get(key)!=new.get(key) for key in set(old)|set(new))
        record=IndexOperationResult(kind,index.version,result.version,affected,(),result.descriptor.digest,self._clock())
        return result,record

    def add(self,index:CanonicalIndex,key:object,reference)->tuple[CanonicalIndex,IndexOperationResult]:
        from .models import IndexKey
        return self.execute(index,IndexOperation(IndexOperationType.ADD,(reference,),(IndexKey(key),),self._clock()))

    def remove(self,index:CanonicalIndex,key:object,reference)->tuple[CanonicalIndex,IndexOperationResult]:
        from .models import IndexKey
        return self.execute(index,IndexOperation(IndexOperationType.REMOVE,(reference,),(IndexKey(key),),self._clock()))

    def replace(self,index:CanonicalIndex,key:object,old_reference,new_reference)->tuple[CanonicalIndex,IndexOperationResult]:
        from .models import IndexKey
        return self.execute(index,IndexOperation(IndexOperationType.REPLACE,(old_reference,new_reference),(IndexKey(key),),self._clock()))

    def rebuild(self,index:CanonicalIndex,entities:tuple[object,...])->tuple[CanonicalIndex,IndexOperationResult]:
        builder=IndexBuilder.from_index(index,clock=self._clock).rebuild(entities); result=builder.build()
        return result,IndexOperationResult(IndexOperationType.REBUILD,index.version,result.version,len(set(v.key.sort_token for v in index.entries)^set(v.key.sort_token for v in result.entries)),(),result.descriptor.digest,self._clock())

    def clear(self,index:CanonicalIndex)->tuple[CanonicalIndex,IndexOperationResult]:
        return self.execute(index,IndexOperation(IndexOperationType.CLEAR,timestamp=self._clock()))

    def merge(self,index:CanonicalIndex,other:CanonicalIndex)->tuple[CanonicalIndex,IndexOperationResult]:
        return self.execute(index,IndexOperation(IndexOperationType.MERGE,timestamp=self._clock()),merge_index=other)


class InMemoryIndexReader:
    def read(self,index:CanonicalIndex,query:IndexQuery,ordering:IndexOrdering=IndexOrdering.ASCENDING)->IndexResult:
        if not isinstance(index,CanonicalIndex) or not isinstance(query,IndexQuery): raise IndexQueryError("reader requires CanonicalIndex and IndexQuery")
        entries=list(index.entries)
        if query.exact_key is not None: entries=[v for v in entries if v.key==query.exact_key]
        if query.exact_keys:
            allowed={v.sort_token for v in query.exact_keys}; entries=[v for v in entries if v.key.sort_token in allowed]
        if query.text_prefix is not None: entries=[v for v in entries if isinstance(v.key.value,str) and v.key.value.startswith(query.text_prefix)]
        if query.lower_bound is not None:
            try: entries=[v for v in entries if query.lower_bound.value<=v.key.value<=query.upper_bound.value]
            except TypeError as error: raise IndexQueryError("range keys are not mutually comparable") from error
        reverse=IndexOrdering(ordering) is IndexOrdering.DESCENDING; entries.sort(key=lambda v:v.key.sort_token,reverse=reverse)
        pairs=[(entry.key,ref) for entry in entries for ref in entry.references]
        if query.reference_type is not None:pairs=[v for v in pairs if v[1].entity_type is query.reference_type]
        if query.version is not None:pairs=[v for v in pairs if v[1].version==query.version]
        if query.namespace is not None:pairs=[v for v in pairs if v[1].namespace==query.namespace]
        unique=[]; seen=set()
        for pair in pairs:
            if pair[1].sort_token not in seen:seen.add(pair[1].sort_token); unique.append(pair)
        total=len(unique); page=unique[query.offset:query.offset+query.limit]
        return IndexResult(tuple(v[1] for v in page),tuple(v[0] for v in page),total,query.limit,query.offset,index.descriptor.digest,{"matched_entries":len(entries)})


IndexOperationExecutor=InMemoryIndexOperations
IndexReader=InMemoryIndexReader
__all__=["InMemoryIndexOperations","InMemoryIndexReader","IndexOperationExecutor","IndexReader"]
