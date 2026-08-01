"""Strict deterministic UTF-8 JSON serialization for canonical query models."""

from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Mapping
from uuid import UUID

from cko.core.documents import DeterministicDocumentSerializer
from cko.core.graph import DeterministicGraphSerializer
from cko.core.knowledge import DeterministicKnowledgeSerializer
from cko.core.relationships import DeterministicRelationshipSerializer

from .contracts import QueryModel, parse_instant, strict
from .enums import (
    QueryConsistency, QueryDirection, QueryOperator, QueryScope, QueryStatus,
    QueryTarget,
)
from .errors import QueryError, QuerySerializationError
from .factory import QueryFactory
from .identity import QueryId, QueryIdentity
from .metadata import QueryMetadata
from .models import (
    CanonicalQuery, QueryCollection, QueryConstraint, QueryDescriptor,
    QueryExpression, QueryFilter, QueryOrdering, QueryPagination,
    QueryProjection, QueryResult, QueryStatistics,
)
from .validator import QueryValidator


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise QuerySerializationError(f"{name} must be an object")
    return value


def _list(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise QuerySerializationError(f"{name} must be an array")
    return value


class DeterministicQuerySerializer:
    """Serialize and restore closed canonical query envelopes."""

    def __init__(self, factory: QueryFactory | None = None,
                 validator: QueryValidator | None = None) -> None:
        self._validator = validator or QueryValidator()
        self._factory = factory or QueryFactory(self._validator)
        self._knowledge = DeterministicKnowledgeSerializer()
        self._documents = DeterministicDocumentSerializer()
        self._relationships = DeterministicRelationshipSerializer()
        self._graphs = DeterministicGraphSerializer()

    def serialize(self, value: QueryModel) -> bytes:
        self._validator.validate(value)
        try:
            return json.dumps(
                value.to_dict(), ensure_ascii=False, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ).encode("utf-8")
        except (TypeError, ValueError, UnicodeError) as error:
            raise QuerySerializationError("query serialization failed") from error

    def deserialize(self, payload: bytes | str) -> QueryModel:
        try:
            encoded = payload.decode("utf-8") if isinstance(payload, bytes) else payload
            if not isinstance(encoded, str):
                raise TypeError
            decoded = json.loads(
                encoded,
                parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
            )
        except (TypeError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
            raise QuerySerializationError("payload must be strict UTF-8 JSON") from error
        try:
            value = self.from_dict(_mapping(decoded, "payload"))
        except QuerySerializationError:
            raise
        except (QueryError, TypeError, ValueError, KeyError, AttributeError) as error:
            raise QuerySerializationError("payload violates the query schema") from error
        if self.serialize(value).decode("utf-8") != encoded:
            raise QuerySerializationError("payload is not canonical JSON")
        return value

    def digest(self, value: QueryModel) -> str:
        return hashlib.sha256(self.serialize(value)).hexdigest()

    def _value(self, value: object) -> object:
        if isinstance(value, list):
            return tuple(self._value(item) for item in value)
        if isinstance(value, Mapping):
            if set(value) == {"__query_scalar__", "value"}:
                kind = value["__query_scalar__"]
                scalar = value["value"]
                if kind == "datetime":
                    return parse_instant(scalar, "query value")
                if kind == "uuid":
                    return UUID(str(scalar))
                if kind == "enum":
                    if not isinstance(scalar, str):
                        raise QuerySerializationError("enum query value must be a string")
                    return scalar
                raise QuerySerializationError("unknown query scalar type")
            if "model" in value:
                model = value.get("model")
                if model == "query_id":
                    return self.from_dict(value)
                raise QuerySerializationError("unsupported model in constraint value")
            return MappingProxyType(dict(sorted(
                (str(key), self._value(item)) for key, item in value.items()
            )))
        return value

    def _embedded(self, payload: object) -> object:
        value = _mapping(payload, "query result item")
        model = value.get("model")
        if not isinstance(model, str):
            raise QuerySerializationError("result item discriminator is required")
        if model == "knowledge_object":
            return self._knowledge.from_dict(value)
        if model == "canonical_document":
            return self._documents.from_dict(value)
        if model == "canonical_relationship":
            return self._relationships.from_dict(value)
        if model == "canonical_graph":
            return self._graphs.from_dict(value)
        raise QuerySerializationError("unsupported canonical query result item")

    def from_dict(self, payload: Mapping[str, object]) -> QueryModel:
        model = payload.get("model")
        if not isinstance(model, str):
            raise QuerySerializationError("model discriminator is required")
        nested = lambda item: self.from_dict(_mapping(item, "nested query model"))

        if model == "query_id":
            value = strict(payload, model, {"value"})
            return QueryId.parse(value["value"])  # type: ignore[arg-type]
        if model == "query_identity":
            value = strict(payload, model, {"logical_id", "canonical_id", "namespace", "name", "version"})
            return QueryIdentity(nested(value["logical_id"]), nested(value["canonical_id"]), value["namespace"], value["name"], value["version"])  # type: ignore[arg-type]
        if model == "query_metadata":
            value = strict(payload, model, {"created_at", "modified_at", "created_by", "status", "tags", "attributes"})
            return QueryMetadata(parse_instant(value["created_at"], "created_at"), parse_instant(value["modified_at"], "modified_at"), value["created_by"], QueryStatus(value["status"]), tuple(_list(value["tags"], "tags")), self._value(_mapping(value["attributes"], "attributes")))  # type: ignore[arg-type]
        if model == "query_constraint":
            value = strict(payload, model, {"operator", "value", "upper_value"})
            return QueryConstraint(QueryOperator(value["operator"]), self._value(value["value"]), self._value(value["upper_value"]))  # type: ignore[arg-type]
        if model == "query_filter":
            value = strict(payload, model, {"field", "constraint"})
            return QueryFilter(value["field"], nested(value["constraint"]))  # type: ignore[arg-type]
        if model == "query_expression":
            value = strict(payload, model, {"operator", "clauses"})
            return QueryExpression(QueryOperator(value["operator"]), tuple(nested(item) for item in _list(value["clauses"], "clauses")))
        if model == "query_ordering":
            value = strict(payload, model, {"field", "direction", "priority"})
            return QueryOrdering(value["field"], QueryDirection(value["direction"]), value["priority"])  # type: ignore[arg-type]
        if model == "query_projection":
            value = strict(payload, model, {"fields", "include_identity", "include_metadata"})
            return QueryProjection(tuple(_list(value["fields"], "fields")), value["include_identity"], value["include_metadata"])  # type: ignore[arg-type]
        if model == "query_pagination":
            value = strict(payload, model, {"limit", "offset", "cursor"})
            return QueryPagination(value["limit"], value["offset"], value["cursor"])  # type: ignore[arg-type]
        if model == "query_descriptor":
            value = strict(payload, model, {"targets", "scope", "consistency", "filters", "expression", "orderings", "projection", "pagination"})
            return QueryDescriptor(tuple(QueryTarget(item) for item in _list(value["targets"], "targets")), QueryScope(value["scope"]), QueryConsistency(value["consistency"]), tuple(nested(item) for item in _list(value["filters"], "filters")), None if value["expression"] is None else nested(value["expression"]), tuple(nested(item) for item in _list(value["orderings"], "orderings")), nested(value["projection"]), nested(value["pagination"]))  # type: ignore[arg-type]
        if model == "canonical_query":
            value = strict(payload, model, {"identity", "metadata", "descriptor"})
            return self._factory.from_parts(identity=nested(value["identity"]), metadata=nested(value["metadata"]), descriptor=nested(value["descriptor"]))  # type: ignore[arg-type]
        if model == "query_statistics":
            value = strict(payload, model, {"total_expected", "total_returned", "logical_time", "metrics"})
            return QueryStatistics(value["total_expected"], value["total_returned"], value["logical_time"], self._value(_mapping(value["metrics"], "metrics")))  # type: ignore[arg-type]
        if model == "query_result":
            value = strict(payload, model, {"query", "items", "status", "total_expected", "total_returned", "logical_time", "statistics", "warnings", "metadata"})
            return self._factory.result_from_parts(query=nested(value["query"]), items=tuple(self._embedded(item) for item in _list(value["items"], "items")), status=QueryStatus(value["status"]), statistics=nested(value["statistics"]), warnings=tuple(_list(value["warnings"], "warnings")), metadata=self._value(_mapping(value["metadata"], "metadata")))  # type: ignore[arg-type]
        if model == "query_collection":
            value = strict(payload, model, {"queries", "name"})
            return self._factory.create_collection(tuple(nested(item) for item in _list(value["queries"], "queries")), value["name"])  # type: ignore[arg-type]
        raise QuerySerializationError(f"unknown model discriminator: {model}")


__all__ = ["DeterministicQuerySerializer"]
