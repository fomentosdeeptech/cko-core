"""Structural validation for technology-neutral canonical queries."""

from __future__ import annotations

import json
from dataclasses import is_dataclass

from .contracts import QueryModel
from .enums import QueryStatus, QueryTarget
from .errors import QueryValidationError
from .models import (
    CanonicalQuery, QueryCollection, QueryDescriptor, QueryExpression,
    QueryFilter, QueryResult,
)


class QueryValidator:
    """Validate schemas, discriminators, duplicates, and structural consistency."""

    def validate(self, value: QueryModel) -> None:
        if not isinstance(value, QueryModel) or not is_dataclass(value):
            raise QueryValidationError("value must be a canonical query dataclass")
        value._validate_schema()
        params = getattr(type(value), "__dataclass_params__", None)
        if params is None or not params.frozen or not hasattr(type(value), "__slots__"):
            raise QueryValidationError("query models must be frozen and slotted")
        if value.model != type(value).discriminator:
            raise QueryValidationError("invalid query model discriminator")
        if isinstance(value, CanonicalQuery):
            self._validate_query(value)
        elif isinstance(value, QueryDescriptor):
            self._validate_descriptor(value)
        elif isinstance(value, QueryExpression):
            self._validate_expression(value)
        elif isinstance(value, QueryCollection):
            identifiers = [query.identity.canonical_id for query in value.queries]
            if len(identifiers) != len(set(identifiers)):
                raise QueryValidationError("collection queries must be unique")
            for query in value.queries:
                self._validate_query(query)
        elif isinstance(value, QueryResult):
            self._validate_result(value)

    @staticmethod
    def _fingerprint(value: QueryModel) -> str:
        return json.dumps(
            value.to_dict(), ensure_ascii=False, allow_nan=False,
            sort_keys=True, separators=(",", ":"),
        )

    def _validate_expression(self, expression: QueryExpression) -> None:
        fingerprints = [self._fingerprint(clause) for clause in expression.clauses]
        if len(fingerprints) != len(set(fingerprints)):
            raise QueryValidationError("expression clauses must not contain duplicates")
        for clause in expression.clauses:
            if isinstance(clause, QueryExpression):
                self._validate_expression(clause)

    def _validate_descriptor(self, descriptor: QueryDescriptor) -> None:
        filter_fingerprints = [self._fingerprint(item) for item in descriptor.filters]
        if len(filter_fingerprints) != len(set(filter_fingerprints)):
            raise QueryValidationError("filters must not contain duplicates")
        if descriptor.expression is not None:
            self._validate_expression(descriptor.expression)
            expression_filters = self._flatten_filters(descriptor.expression)
            expression_fingerprints = {self._fingerprint(item) for item in expression_filters}
            if expression_fingerprints.intersection(filter_fingerprints):
                raise QueryValidationError("filters must not be duplicated in expression")
        fields = [ordering.field for ordering in descriptor.orderings]
        priorities = [ordering.priority for ordering in descriptor.orderings]
        if len(fields) != len(set(fields)):
            raise QueryValidationError("ordering fields must be unique")
        if len(priorities) != len(set(priorities)):
            raise QueryValidationError("ordering priorities must be unique")

    def _validate_query(self, query: CanonicalQuery) -> None:
        if query.metadata.status not in {QueryStatus.DRAFT, QueryStatus.READY}:
            raise QueryValidationError("canonical query status must be draft or ready")
        self._validate_descriptor(query.descriptor)

    def _validate_result(self, result: QueryResult) -> None:
        self._validate_query(result.query)
        if result.status not in {
            QueryStatus.COMPLETED, QueryStatus.PARTIAL, QueryStatus.EMPTY,
            QueryStatus.FAILED,
        }:
            raise QueryValidationError("query result has an invalid result status")
        if result.status is QueryStatus.EMPTY and result.items:
            raise QueryValidationError("empty result cannot contain items")
        target_by_type = {
            "KnowledgeObject": QueryTarget.KNOWLEDGE_OBJECT,
            "CanonicalDocument": QueryTarget.CANONICAL_DOCUMENT,
            "CanonicalRelationship": QueryTarget.CANONICAL_RELATIONSHIP,
            "CanonicalGraph": QueryTarget.CANONICAL_GRAPH,
        }
        targets = set(result.query.descriptor.targets)
        for item in result.items:
            target = target_by_type.get(type(item).__name__)
            if target not in targets:
                raise QueryValidationError("result item does not match query targets")
        identifiers = [self._item_identity(item) for item in result.items]
        if len(identifiers) != len(set(identifiers)):
            raise QueryValidationError("result items must be unique")

    @staticmethod
    def _flatten_filters(expression: QueryExpression) -> tuple[QueryFilter, ...]:
        result: list[QueryFilter] = []
        for clause in expression.clauses:
            if isinstance(clause, QueryFilter):
                result.append(clause)
            else:
                result.extend(QueryValidator._flatten_filters(clause))
        return tuple(result)

    @staticmethod
    def _item_identity(item: object) -> object:
        identity = getattr(item, "identity", None)
        canonical_id = getattr(identity, "canonical_id", None)
        if canonical_id is None:
            canonical_id = getattr(identity, "document_id", None)
        if canonical_id is None:
            raise QueryValidationError("result item lacks canonical identity")
        return type(item).__name__, str(canonical_id)


__all__ = ["QueryValidator"]
