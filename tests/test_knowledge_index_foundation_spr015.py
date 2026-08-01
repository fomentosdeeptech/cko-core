"""Dedicated acceptance suite for SPR-015 Knowledge Index Foundation."""

from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from uuid import uuid4

import pytest

import cko.core as core
from cko.core.exceptions import CKOError
from cko.core.index import *
from cko.core.query import QueryFactory, QueryTarget

NOW=datetime(2026,7,26,12,0,tzinfo=UTC)


@pytest.fixture
def factory():return IndexFactory(clock=lambda:NOW)


@pytest.fixture
def definition(factory):
    return factory.create_definition(name="by namespace",namespace="cko.test",index_type=IndexType.NAMESPACE,
        targets=tuple(IndexTarget),fields=(IndexField("namespace"),))


def ref(value="1",target=IndexTarget.KNOWLEDGE_OBJECT,namespace="cko.test",version="1.0.0"):
    return IndexReference(namespace,value,target,version,target.value,"a"*64,{"label":"mínimo"})


def built(factory,definition):
    builder=IndexBuilder(definition,factory=factory,clock=lambda:NOW)
    builder.add_reference("alpha",ref("1"));builder.add_reference("beta",ref("2"))
    return builder.build()


def test_public_models_are_frozen_slotted_and_present():
    models=(IndexId,IndexIdentity,IndexMetadata,IndexKey,IndexReference,IndexEntry,IndexField,
        IndexDefinition,IndexVersion,IndexStatistics,IndexSnapshot,IndexDescriptor,CanonicalIndex,
        IndexCollection,IndexOperation,IndexOperationResult,IndexQuery,IndexResult)
    for model in models:
        assert is_dataclass(model);assert model.__dataclass_params__.frozen;assert hasattr(model,"__slots__")
        assert getattr(core.index,model.__name__) is model


def test_all_enums_and_required_values():
    assert {x.name for x in IndexType}>={"IDENTITY","NAMESPACE","ENTITY_TYPE","DOCUMENT_TYPE","RELATIONSHIP_TYPE","GRAPH_NODE_TYPE","STATUS","CATEGORY","AUTHOR","CREATOR","ORGANIZATION","SOURCE","LANGUAGE","VERSION","TAG","KEYWORD","ATTRIBUTE","PROPERTY","CREATED_AT","UPDATED_AT","CHECKSUM","CUSTOM"}
    assert {x.name for x in IndexTarget}=={"KNOWLEDGE_OBJECT","CANONICAL_DOCUMENT","CANONICAL_RELATIONSHIP","CANONICAL_GRAPH","CANONICAL_QUERY"}
    for enum in (IndexStatus,IndexOperationType,IndexSnapshotType,IndexConsistency,IndexValuePolicy,IndexMultiplicity,IndexOrdering,IndexKeyType):
        assert issubclass(enum,(str,Enum));assert all(isinstance(x.value,str) for x in enum)


def test_definition_identity_is_deterministic(factory):
    values=dict(name="tags",namespace="cko.test",index_type=IndexType.TAG,targets=(IndexTarget.KNOWLEDGE_OBJECT,),fields=(IndexField("tags"),),multiplicity=IndexMultiplicity.MULTIPLE)
    assert factory.create_definition(**values).definition_id==factory.create_definition(**values).definition_id


def test_factory_is_required_for_aggregates(definition):
    with pytest.raises(IndexFactoryError):IndexDefinition(definition.definition_id,"x","n",IndexType.TAG,(IndexTarget.KNOWLEDGE_OBJECT,),(IndexField("tags"),))
    with pytest.raises(IndexFactoryError):IndexCollection()


def test_key_types_normalization_and_rejections():
    values=("á",1,Decimal("1.20"),True,uuid4(),NOW,IndexStatus.ACTIVE,"a"*64,("x",1))
    expected=(IndexKeyType.TEXT,IndexKeyType.INTEGER,IndexKeyType.DECIMAL,IndexKeyType.BOOLEAN,IndexKeyType.UUID,IndexKeyType.DATETIME,IndexKeyType.ENUM,IndexKeyType.SHA256,IndexKeyType.SEQUENCE)
    assert tuple(IndexKey(v,IndexKeyType.SHA256 if i==7 else None).key_type for i,v in enumerate(values))==expected
    for value in (float("nan"),float("inf"),{},object(),()):
        with pytest.raises(IndexValidationError):IndexKey(value)


def test_deep_freeze(definition):
    source={"nested":["a",{"b":1}]}
    value=IndexReference("n","id",IndexTarget.CANONICAL_QUERY,"1.0.0","canonical_query",metadata=source)
    source["nested"].append("changed")
    assert value.metadata["nested"]==("a",value.metadata["nested"][1])
    with pytest.raises(TypeError):value.metadata["new"]=1
    with pytest.raises(FrozenInstanceError):definition.name="changed"


def test_field_grammar_is_closed():
    for path in ("sql(select)","$.tags","attributes","unknown","a..b"):
        with pytest.raises(IndexDefinitionError):IndexField(path)
    assert IndexField("attributes.owner").path=="attributes.owner"


def test_definition_rejects_duplicates_and_incompatible_unique(factory):
    with pytest.raises(IndexDefinitionError):factory.create_definition(name="x",namespace="n",index_type=IndexType.TAG,targets=(),fields=(IndexField("tags"),))
    with pytest.raises(IndexConsistencyError):factory.create_definition(name="x",namespace="n",index_type=IndexType.TAG,targets=(IndexTarget.KNOWLEDGE_OBJECT,),fields=(IndexField("tags"),),unique=True,multiplicity=IndexMultiplicity.MULTIPLE)


def test_empty_build_and_builder_operations(factory,definition):
    empty=IndexBuilder(definition,factory=factory,clock=lambda:NOW).build();assert empty.entries==();assert empty.descriptor.reference_count==0
    index=built(factory,definition);assert len(index.entries)==2;assert index.entries[0].key.value=="alpha"
    b=IndexBuilder.from_index(index,factory=factory,clock=lambda:NOW);b.remove_reference("alpha",ref("1"));after=b.build();assert len(after.entries)==1
    b=IndexBuilder.from_index(after,factory=factory,clock=lambda:NOW);b.replace(ref("2"),ref("3"),"beta");assert b.build().entries[0].references[0].canonical_id=="3"
    assert IndexBuilder.from_index(index,factory=factory,clock=lambda:NOW).clear().build().entries==()


def test_unique_index_rejects_collision(factory):
    d=factory.create_definition(name="id",namespace="n",index_type=IndexType.IDENTITY,targets=(IndexTarget.KNOWLEDGE_OBJECT,),fields=(IndexField("identity"),),unique=True)
    b=IndexBuilder(d,factory=factory,clock=lambda:NOW).add_reference("x",ref("1",namespace="n"))
    with pytest.raises(IndexOperationError):b.add_reference("x",ref("2",namespace="n"))


def test_target_compatibility(factory):
    d=factory.create_definition(name="query",namespace="n",index_type=IndexType.NAMESPACE,targets=(IndexTarget.CANONICAL_QUERY,),fields=(IndexField("namespace"),))
    with pytest.raises(IndexValidationError):IndexBuilder(d,factory=factory).add_reference("n",ref())


def test_build_from_canonical_query(factory):
    query=QueryFactory(clock=lambda:NOW).create(namespace="queries",name="q",created_by="tester",targets=(QueryTarget.KNOWLEDGE_OBJECT,))
    d=factory.create_definition(name="query namespace",namespace="indexes",index_type=IndexType.NAMESPACE,targets=(IndexTarget.CANONICAL_QUERY,),fields=(IndexField("namespace"),))
    index=IndexBuilder(d,factory=factory,clock=lambda:NOW).build((query,))
    assert index.entries[0].key.value=="queries";assert index.entries[0].references[0].entity_type is IndexTarget.CANONICAL_QUERY


def test_merge_and_incompatible_merge(factory,definition):
    left=IndexBuilder(definition,factory=factory,clock=lambda:NOW).add_reference("a",ref("1")).build()
    right=IndexBuilder(definition,factory=factory,clock=lambda:NOW).add_reference("b",ref("2")).build()
    assert len(IndexBuilder.from_index(left,factory=factory,clock=lambda:NOW).merge(right).build().entries)==2
    other=factory.create_definition(name="other",namespace="n",index_type=IndexType.TAG,targets=(IndexTarget.KNOWLEDGE_OBJECT,),fields=(IndexField("tags"),))
    with pytest.raises(IndexOperationError):IndexBuilder.from_index(left).merge(factory.create_index(other))


def test_structural_reads(factory,definition):
    index=built(factory,definition);reader=InMemoryIndexReader()
    assert reader.read(index,IndexQuery(exact_key=IndexKey("alpha"))).references==(ref("1"),)
    assert reader.read(index,IndexQuery(text_prefix="b")).references==(ref("2"),)
    assert reader.read(index,IndexQuery(lower_bound=IndexKey("alpha"),upper_bound=IndexKey("beta"))).total==2
    assert reader.read(index,IndexQuery(limit=1,offset=1)).references==(ref("2"),)
    assert reader.read(index,IndexQuery(namespace="cko.test",reference_type=IndexTarget.KNOWLEDGE_OBJECT,version="1.0.0")).total==2


def test_invalid_queries():
    with pytest.raises(IndexQueryError):IndexQuery(exact_key=IndexKey("x"),exact_keys=(IndexKey("x"),))
    with pytest.raises(IndexQueryError):IndexQuery(lower_bound=IndexKey(1))
    with pytest.raises(IndexQueryError):IndexQuery(lower_bound=IndexKey(1),upper_bound=IndexKey("x"))
    with pytest.raises(IndexQueryError):IndexQuery(limit=0)


def test_statistics_and_snapshot(factory,definition):
    index=built(factory,definition);stats=DefaultIndexStatisticsProvider(lambda:NOW).calculate(index)
    assert (stats.total_keys,stats.total_references,stats.total_unique_references)==(2,2,2)
    snapshot=factory.create_snapshot(index);assert snapshot.digest==index.descriptor.digest;IndexValidator().validate(snapshot,index=index)
    object.__setattr__(snapshot,"digest","0"*64)
    with pytest.raises(IndexConsistencyError):IndexValidator().validate(snapshot,index=index)


def test_operation_executor(factory,definition):
    index=factory.create_index(definition);op=IndexOperation(IndexOperationType.ADD,(ref(),),(IndexKey("a"),),NOW)
    result,record=InMemoryIndexOperations(lambda:NOW).execute(index,op)
    assert len(result.entries)==1;assert record.operation is IndexOperationType.ADD;assert record.affected_entries==1
    cleared,record=InMemoryIndexOperations(lambda:NOW).execute(result,IndexOperation(IndexOperationType.CLEAR,timestamp=NOW))
    assert cleared.entries==();assert record.affected_entries==1


def test_all_structural_operation_paths(factory,definition):
    ops=InMemoryIndexOperations(lambda:NOW);empty=factory.create_index(definition)
    added,_=ops.add(empty,"a",ref("1"));replaced,_=ops.replace(added,"a",ref("1"),ref("2"))
    assert replaced.entries[0].references==(ref("2"),)
    removed,_=ops.remove(replaced,"a",ref("2"));assert removed.entries==()
    left,_=ops.add(empty,"a",ref("1"));right,_=ops.add(empty,"b",ref("2"))
    merged,record=ops.merge(left,right);assert len(merged.entries)==2;assert record.operation is IndexOperationType.MERGE
    rebuilt,_=ops.execute(left,IndexOperation(IndexOperationType.REBUILD,(ref("2"),),(IndexKey("b"),),NOW));assert rebuilt.entries[0].key.value=="b"
    with pytest.raises(IndexOperationError):ops.execute(empty,IndexOperation(IndexOperationType.MERGE,timestamp=NOW))
    with pytest.raises(IndexOperationError):ops.execute(empty,IndexOperation(IndexOperationType.REBUILD,(ref(),),(),NOW))
    with pytest.raises(IndexOperationError):ops.execute(empty,IndexOperation(IndexOperationType.REPLACE,(ref(),),(),NOW))


def test_builder_policies_services_and_no_effect(factory):
    multi=factory.create_definition(name="tags",namespace="n",index_type=IndexType.TAG,targets=(IndexTarget.CANONICAL_QUERY,),fields=(IndexField("tags"),),multiplicity=IndexMultiplicity.MULTIPLE,case_sensitive=False)
    query=QueryFactory(clock=lambda:NOW).create(namespace="queries",name="q",created_by="tester",targets=(QueryTarget.KNOWLEDGE_OBJECT,),tags=("Alpha","Beta"))
    builder=IndexBuilder(multi,factory=factory,clock=lambda:NOW).add(query)
    assert [v.key.value for v in builder.build().entries]==["Alpha","Beta"]
    assert builder.snapshot().entry_count==2;assert builder.statistics().total_keys==2
    with pytest.raises(IndexOperationError):builder.remove(ref("absent",IndexTarget.CANONICAL_QUERY,"queries"))


def test_reader_descending_and_invalid_subject(factory,definition):
    reader=InMemoryIndexReader();index=built(factory,definition)
    assert reader.read(index,IndexQuery(limit=1),IndexOrdering.DESCENDING).matched_keys[0].value=="beta"
    with pytest.raises(IndexQueryError):reader.read("not-index",IndexQuery())


def test_validator_detects_digest_tampering(factory,definition):
    index=built(factory,definition);object.__setattr__(index.descriptor,"digest","0"*64)
    with pytest.raises(IndexConsistencyError):IndexValidator().validate(index)


def test_serializer_round_trip_all_public_models(factory,definition):
    index=built(factory,definition);snapshot=factory.create_snapshot(index);stats=snapshot.statistics
    query=IndexQuery(exact_key=IndexKey((uuid4(),NOW,Decimal("1.2"))))
    result=InMemoryIndexReader().read(index,IndexQuery(limit=1));operation=IndexOperation(IndexOperationType.ADD,(ref(),),(IndexKey("a"),),NOW)
    opresult=IndexOperationResult(IndexOperationType.ADD,index.version,index.version,1,(),index.descriptor.digest,NOW)
    values=(IndexId.new(),index.identity,index.metadata,IndexKey("x"),ref(),index.entries[0],IndexField("namespace"),definition,index.version,stats,snapshot,index.descriptor,index,factory.create_collection((index,),"all"),operation,opresult,query,result)
    serializer=DeterministicIndexSerializer(factory)
    for value in values:assert serializer.deserialize(serializer.serialize(value))==value


def test_serializer_closed_schema_and_canonical_json(factory,definition):
    serializer=DeterministicIndexSerializer(factory);payload=serializer.serialize(definition)
    with pytest.raises(IndexSerializationError):serializer.deserialize(payload+b" ")
    with pytest.raises(IndexSerializationError):serializer.deserialize(b'{"model":"unknown","schema_version":"1.0"}')
    text=payload.decode().replace('"name":"by namespace"','"extra":1,"name":"by namespace"')
    with pytest.raises(IndexSerializationError):serializer.deserialize(text)
    with pytest.raises(IndexSerializationError):serializer.deserialize(b'{"model":"index_key","schema_version":"2.0","value":1,"key_type":"integer"}')
    with pytest.raises(IndexSerializationError):serializer.deserialize(b'{"model":"index_key","schema_version":"1.0","value":NaN,"key_type":"decimal"}')


def test_public_root_aliases_and_errors():
    assert core.CanonicalIndexType is IndexType;assert core.CanonicalIndexQuery is IndexQuery;assert core.CanonicalIndexResult is IndexResult
    for error in (IndexError,IndexValidationError,IndexSerializationError,IndexFactoryError,IndexIdentityError,IndexDefinitionError,IndexOperationError,IndexConsistencyError,IndexQueryError):assert issubclass(error,CKOError)


def test_no_prohibited_imports():
    from pathlib import Path
    root=Path(__file__).parents[1]/"src"/"cko"/"core"/"index"
    content="\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))
    for name in ("sqlite3","elasticsearch","opensearch","networkx","redis","mongodb","numpy","sklearn","openai"):
        assert f"import {name}" not in content and f"from {name}" not in content
