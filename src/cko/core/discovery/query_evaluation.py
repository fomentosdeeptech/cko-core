"""Canonical deterministic evaluation of query plans over in-memory subjects."""

from __future__ import annotations

from collections.abc import AsyncIterable, Iterable, Mapping, Sequence
from dataclasses import dataclass, fields, is_dataclass
from functools import cmp_to_key
from typing import Final

from cko.core.logging import get_logger

from .cancellation import CancellationToken
from .foundation_errors import DiscoveryCancelledError
from .query_evaluation_contracts import (
    AttributeResolver,
    AttributeValue,
    MappingQueryEvaluationSubject,
    QueryEvaluationSubject,
)
from .query_evaluation_errors import (
    AttributeResolutionError,
    FilterGroupEvaluationError,
    InvalidQueryEvaluationSubjectError,
    PredicateEvaluationError,
    QueryEvaluationCancelledError,
    QueryEvaluationError,
    QueryEvaluationLimitError,
    QueryOrderingEvaluationError,
    QueryPaginationEvaluationError,
    QueryProjectionEvaluationError,
)
from .query_evaluation_models import (
    EvaluationErrorBehavior,
    IncompatibleTypeBehavior,
    MissingAttributeBehavior,
    OrderingValuePosition,
    PredicateEvaluationRecord,
    ProjectedQueryItem,
    QueryEvaluationContext,
    QueryEvaluationPolicy,
    QueryEvaluationResult,
    QueryMatchResult,
)
from .query_models import (
    FilterGroup,
    FilterGroupOperator,
    QueryExpression,
    QueryFilter,
    QueryOperator,
    QueryOrdering,
    QueryOrderingDirection,
    QueryPagination,
    QueryPlan,
    QueryProjection,
)


_MISSING: Final[object] = object()


class DefaultAttributeResolver:
    """Resolve dotted public paths from mappings and public CKO dataclasses."""

    def resolve(self, subject: object, attribute: str) -> AttributeValue:
        """Resolve without private access, unrestricted reflection or calls."""
        if not isinstance(attribute, str) or not attribute.strip():
            raise AttributeResolutionError("attribute must be a non-empty string")
        parts = tuple(attribute.strip().split("."))
        if any(not part or part.startswith("_") for part in parts):
            raise AttributeResolutionError("private or empty path segments are forbidden")
        current = subject.source if isinstance(subject, QueryEvaluationSubject) else subject
        traversed: list[str] = []
        for part in parts:
            traversed.append(part)
            if isinstance(current, Mapping):
                if part not in current:
                    return AttributeValue(attribute, False, None, tuple(traversed))
                current = current[part]
                continue
            if is_dataclass(current) and type(current).__module__.startswith("cko.core"):
                public_fields = {item.name for item in fields(current)}
                if part not in public_fields or part.startswith("_"):
                    return AttributeValue(attribute, False, None, tuple(traversed))
                current = object.__getattribute__(current, part)
                continue
            return AttributeValue(attribute, False, None, tuple(traversed))
        return AttributeValue(attribute, True, current, parts)


def _numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _equal(left: object, right: object) -> bool:
    if _numeric(left) and _numeric(right):
        return bool(left == right)
    if type(left) is not type(right):
        raise TypeError("exact comparison requires compatible types")
    return bool(left == right)


def _relational(left: object, right: object, operator: QueryOperator) -> bool:
    compatible = (_numeric(left) and _numeric(right)) or (
        type(left) is type(right) and isinstance(left, str)
    )
    if not compatible:
        raise TypeError("relational comparison requires compatible numbers or strings")
    if operator is QueryOperator.GREATER_THAN:
        return bool(left > right)
    if operator is QueryOperator.GREATER_OR_EQUAL:
        return bool(left >= right)
    if operator is QueryOperator.LOWER_THAN:
        return bool(left < right)
    return bool(left <= right)


class QueryPredicateEvaluator:
    """Evaluate every homologated atomic query operator with explicit semantics."""

    def __init__(
        self,
        resolver: AttributeResolver | None = None,
        policy: QueryEvaluationPolicy | None = None,
    ) -> None:
        """Create an evaluator with injectable resolution and safety policy."""
        self._resolver = resolver or DefaultAttributeResolver()
        self._policy = policy or QueryEvaluationPolicy()

    def evaluate(
        self, subject: QueryEvaluationSubject, query_filter: QueryFilter
    ) -> PredicateEvaluationRecord:
        """Evaluate one predicate and return its complete audit record."""
        resolution = self._resolver.resolve(subject, query_filter.attribute)
        operator = query_filter.operator
        if operator is QueryOperator.EXISTS:
            return self._record(query_filter, resolution, resolution.exists, "EXISTS")
        if operator is QueryOperator.NOT_EXISTS:
            return self._record(
                query_filter, resolution, not resolution.exists, "NOT_EXISTS"
            )
        if not resolution.exists:
            if self._policy.missing_attribute is MissingAttributeBehavior.ERROR:
                raise PredicateEvaluationError(
                    f"attribute {query_filter.attribute!r} is missing"
                )
            return self._record(
                query_filter, resolution, False, "ATTRIBUTE_MISSING"
            )
        try:
            matched = self._apply(operator, resolution.value, query_filter.value)
        except (TypeError, ValueError) as error:
            if self._policy.incompatible_type is IncompatibleTypeBehavior.NO_MATCH:
                return self._record(
                    query_filter, resolution, False, "INCOMPATIBLE_TYPE"
                )
            raise PredicateEvaluationError(
                f"incompatible values for operator {operator.value}"
            ) from error
        return self._record(
            query_filter,
            resolution,
            matched,
            "PREDICATE_MATCHED" if matched else "PREDICATE_REJECTED",
        )

    @staticmethod
    def _apply(operator: QueryOperator, observed: object, expected: object) -> bool:
        if operator is QueryOperator.EQUALS:
            return _equal(observed, expected)
        if operator is QueryOperator.NOT_EQUALS:
            return not _equal(observed, expected)
        if operator in {
            QueryOperator.GREATER_THAN,
            QueryOperator.GREATER_OR_EQUAL,
            QueryOperator.LOWER_THAN,
            QueryOperator.LOWER_OR_EQUAL,
        }:
            return _relational(observed, expected, operator)
        if operator is QueryOperator.CONTAINS:
            if isinstance(observed, str) and isinstance(expected, str):
                return expected in observed
            if isinstance(observed, Mapping):
                return any(_equal(key, expected) for key in observed)
            if isinstance(observed, Sequence) and not isinstance(observed, str):
                return any(_equal(item, expected) for item in observed)
            raise TypeError("contains requires a string, sequence or mapping")
        if operator is QueryOperator.STARTS_WITH:
            if not isinstance(observed, str) or not isinstance(expected, str):
                raise TypeError("starts_with requires strings")
            return observed.startswith(expected)
        if operator is QueryOperator.ENDS_WITH:
            if not isinstance(observed, str) or not isinstance(expected, str):
                raise TypeError("ends_with requires strings")
            return observed.endswith(expected)
        if operator in {QueryOperator.IN, QueryOperator.NOT_IN}:
            if not isinstance(expected, tuple):
                raise TypeError("in operators require a canonical sequence")
            contained = any(_equal(observed, item) for item in expected)
            return contained if operator is QueryOperator.IN else not contained
        raise ValueError(f"unsupported operator {operator.value}")

    @staticmethod
    def _record(
        query_filter: QueryFilter,
        resolution: AttributeValue,
        matched: bool,
        code: str,
    ) -> PredicateEvaluationRecord:
        explanations = {
            "EXISTS": "logical attribute is present",
            "NOT_EXISTS": "logical attribute is absent",
            "ATTRIBUTE_MISSING": "missing attribute evaluated as no match by policy",
            "INCOMPATIBLE_TYPE": "incompatible type evaluated as no match by policy",
            "PREDICATE_MATCHED": "observed value satisfies the predicate",
            "PREDICATE_REJECTED": "observed value does not satisfy the predicate",
        }
        return PredicateEvaluationRecord(
            attribute=query_filter.attribute,
            operator=query_filter.operator.value,
            expected_value=query_filter.value,
            observed_value=resolution.value,
            matched=matched,
            attribute_exists=resolution.exists,
            justification=explanations[code],
            code=code,
            logical_path=resolution.logical_path,
        )


@dataclass(frozen=True, slots=True)
class _GroupOutcome:
    matched: bool
    records: tuple[PredicateEvaluationRecord, ...]
    justifications: tuple[str, ...]


class FilterGroupEvaluator:
    """Recursively evaluate AND, OR and NOT with auditable short-circuiting."""

    def __init__(self, predicate_evaluator: QueryPredicateEvaluator) -> None:
        """Create a group evaluator from the canonical predicate evaluator."""
        self._predicate_evaluator = predicate_evaluator

    def evaluate(
        self, subject: QueryEvaluationSubject, expression: QueryExpression
    ) -> _GroupOutcome:
        """Evaluate an atomic predicate or recursive logical group."""
        if isinstance(expression, QueryFilter):
            record = self._predicate_evaluator.evaluate(subject, expression)
            return _GroupOutcome(record.matched, (record,), ())
        if not isinstance(expression, FilterGroup):
            raise FilterGroupEvaluationError("unsupported filter expression")
        records: list[PredicateEvaluationRecord] = []
        reasons: list[str] = []
        if expression.operator is FilterGroupOperator.NOT:
            nested = self.evaluate(subject, expression.filters[0])
            return _GroupOutcome(
                not nested.matched,
                nested.records,
                (*nested.justifications, "NOT inverted the nested decision"),
            )
        desired = expression.operator is FilterGroupOperator.AND
        for index, member in enumerate(expression.filters):
            nested = self.evaluate(subject, member)
            records.extend(nested.records)
            reasons.extend(nested.justifications)
            if expression.operator is FilterGroupOperator.AND and not nested.matched:
                reasons.append(f"AND short-circuited after member {index}")
                return _GroupOutcome(False, tuple(records), tuple(reasons))
            if expression.operator is FilterGroupOperator.OR and nested.matched:
                reasons.append(f"OR short-circuited after member {index}")
                return _GroupOutcome(True, tuple(records), tuple(reasons))
        return _GroupOutcome(desired, tuple(records), tuple(reasons))


class QueryProjectionEngine:
    """Produce immutable explicit projections after subject approval."""

    def __init__(self, resolver: AttributeResolver) -> None:
        """Create a projection engine using the safe attribute resolver."""
        self._resolver = resolver

    def project(
        self,
        subject: QueryEvaluationSubject,
        projections: tuple[QueryProjection, ...],
        match: QueryMatchResult,
    ) -> ProjectedQueryItem:
        """Project declared logical names without modifying the source."""
        selected: dict[str, object] = {}
        missing: list[str] = []
        try:
            for projection in projections:
                value = self._resolver.resolve(subject, projection.attribute)
                if value.exists:
                    selected[projection.attribute] = value.value
                else:
                    selected[projection.attribute] = None
                    missing.append(projection.attribute)
            return ProjectedQueryItem(
                logical_identity=match.logical_identity,
                attributes=selected,
                missing_attributes=tuple(missing),
                evaluation_metadata={
                    "evaluated_filters": match.evaluated_filters,
                    "approved_filters": match.approved_filters,
                },
            )
        except QueryEvaluationError:
            raise
        except Exception as error:
            raise QueryProjectionEvaluationError(
                "subject projection failed"
            ) from error


@dataclass(frozen=True, slots=True)
class _ApprovedSubject:
    subject: QueryEvaluationSubject
    match: QueryMatchResult
    projection: ProjectedQueryItem | None


class QueryOrderingEngine:
    """Apply prioritized stable ordering with deterministic identity ties."""

    def __init__(
        self, resolver: AttributeResolver, policy: QueryEvaluationPolicy
    ) -> None:
        """Create an ordering engine with explicit null and missing positions."""
        self._resolver = resolver
        self._policy = policy

    def order(
        self,
        items: Iterable[_ApprovedSubject],
        ordering: tuple[QueryOrdering, ...],
    ) -> tuple[_ApprovedSubject, ...]:
        """Order approved subjects and resolve all ties by logical identity."""
        materialized = tuple(items)
        try:
            return tuple(sorted(materialized, key=cmp_to_key(
                lambda left, right: self._compare(left, right, ordering)
            )))
        except QueryOrderingEvaluationError:
            raise
        except Exception as error:
            raise QueryOrderingEvaluationError("query ordering failed") from error

    def _compare(
        self,
        left: _ApprovedSubject,
        right: _ApprovedSubject,
        ordering: tuple[QueryOrdering, ...],
    ) -> int:
        for clause in sorted(ordering, key=lambda item: item.priority):
            left_value = self._resolver.resolve(left.subject, clause.attribute)
            right_value = self._resolver.resolve(right.subject, clause.attribute)
            comparison, positioned = self._compare_values(left_value, right_value)
            if comparison:
                if (
                    not positioned
                    and clause.direction is QueryOrderingDirection.DESCENDING
                ):
                    comparison *= -1
                return comparison
        return (left.match.logical_identity > right.match.logical_identity) - (
            left.match.logical_identity < right.match.logical_identity
        )

    def _compare_values(
        self, left: AttributeValue, right: AttributeValue
    ) -> tuple[int, bool]:
        left_rank = self._position_rank(left)
        right_rank = self._position_rank(right)
        if left_rank != right_rank:
            return (-1 if left_rank < right_rank else 1), True
        if left_rank != 0:
            return 0, True
        try:
            if _equal(left.value, right.value):
                return 0, False
            if (_numeric(left.value) and _numeric(right.value)) or (
                isinstance(left.value, str) and isinstance(right.value, str)
            ):
                return (-1 if left.value < right.value else 1), False
        except TypeError as error:
            raise QueryOrderingEvaluationError(
                "ordering values have incompatible types"
            ) from error
        raise QueryOrderingEvaluationError("ordering values have incompatible types")

    def _position_rank(self, value: AttributeValue) -> int:
        if not value.exists:
            position = self._policy.missing_ordering_position
            return -1 if position is OrderingValuePosition.FIRST else 1
        if value.value is None:
            position = self._policy.none_ordering_position
            return -1 if position is OrderingValuePosition.FIRST else 1
        return 0


class QueryPaginationEngine:
    """Apply normalized offset and limit after filtering and ordering."""

    @staticmethod
    def paginate(
        items: tuple[_ApprovedSubject, ...], pagination: QueryPagination | None
    ) -> tuple[tuple[_ApprovedSubject, ...], int, int | None]:
        """Return a deterministic page plus its applied normalized boundaries."""
        if pagination is None:
            return items, 0, None
        offset = pagination.offset
        if offset is None and pagination.page is not None:
            offset = (pagination.page - 1) * pagination.page_size
        offset = offset or 0
        limit = pagination.limit or pagination.page_size
        if offset < 0 or (limit is not None and limit < 1):
            raise QueryPaginationEvaluationError("pagination is not normalized")
        end = None if limit is None else offset + limit
        return items[offset:end], offset, limit


class QueryEvaluationEngine:
    """Canonical synchronous and asynchronous in-memory query evaluation engine."""

    def __init__(
        self,
        *,
        attribute_resolver: AttributeResolver | None = None,
        policy: QueryEvaluationPolicy | None = None,
    ) -> None:
        """Create an engine from public injectable strategies and policy."""
        self._resolver = attribute_resolver or DefaultAttributeResolver()
        self._policy = policy or QueryEvaluationPolicy()
        predicate = QueryPredicateEvaluator(self._resolver, self._policy)
        self._groups = FilterGroupEvaluator(predicate)
        self._projection = QueryProjectionEngine(self._resolver)
        self._ordering = QueryOrderingEngine(self._resolver, self._policy)
        self._pagination = QueryPaginationEngine()
        self._logger = get_logger("core.discovery.query_evaluation")

    def evaluate(
        self,
        plan: QueryPlan,
        subjects: Iterable[QueryEvaluationSubject],
        *,
        context: QueryEvaluationContext | None = None,
        cancellation_token: CancellationToken | None = None,
    ) -> QueryEvaluationResult:
        """Synchronously evaluate an iterable using only in-memory operations."""
        if not isinstance(plan, QueryPlan):
            raise TypeError("plan must be QueryPlan")
        execution_context = context or QueryEvaluationContext(
            correlation_id=plan.query_id, actor="cko.core"
        )
        token = cancellation_token or execution_context.cancellation_token
        self._log("started", plan.query_id, {})
        try:
            result = self._consume_synchronous(
                plan, subjects, execution_context, token
            )
        except QueryEvaluationCancelledError:
            self._log("cancelled", plan.query_id, {})
            raise
        except QueryEvaluationError:
            self._log("failed", plan.query_id, {}, level="error")
            raise
        except Exception as error:
            self._log("failed", plan.query_id, {}, level="error")
            raise QueryEvaluationError("query evaluation failed") from error
        self._log(
            "completed",
            plan.query_id,
            {
                "total_evaluated": result.total_evaluated,
                "total_matched": result.total_matched,
                "total_rejected": result.total_rejected,
                "total_returned": result.total_returned,
            },
        )
        return result

    async def evaluate_async(
        self,
        plan: QueryPlan,
        subjects: AsyncIterable[QueryEvaluationSubject],
        *,
        context: QueryEvaluationContext | None = None,
        cancellation_token: CancellationToken | None = None,
    ) -> QueryEvaluationResult:
        """Evaluate an AsyncIterable without threads or infrastructure access."""
        if not isinstance(plan, QueryPlan):
            raise TypeError("plan must be QueryPlan")
        execution_context = context or QueryEvaluationContext(
            correlation_id=plan.query_id, actor="cko.core"
        )
        token = cancellation_token or execution_context.cancellation_token
        approved: list[_ApprovedSubject] = []
        matches: list[QueryMatchResult] = []
        errors: list[str] = []
        self._log("started", plan.query_id, {})
        try:
            async for raw_subject in subjects:
                self._check_cancelled(token)
                if len(matches) >= self._policy.max_subjects:
                    raise QueryEvaluationLimitError(
                        f"subject limit {self._policy.max_subjects} exceeded"
                    )
                subject = self._validate_subject(raw_subject, len(matches))
                item = self._evaluate_one(
                    plan, subject, execution_context, matches, errors
                )
                if item is not None:
                    approved.append(item)
            self._log(
                "received", plan.query_id, {"total_received": len(matches)}
            )
            result = self._finalize(
                plan, execution_context, approved, matches, errors
            )
        except QueryEvaluationCancelledError:
            self._log("cancelled", plan.query_id, {})
            raise
        except QueryEvaluationError:
            self._log("failed", plan.query_id, {}, level="error")
            raise
        except Exception as error:
            self._log("failed", plan.query_id, {}, level="error")
            raise QueryEvaluationError(
                "asynchronous query evaluation failed"
            ) from error
        self._log_completion(result)
        return result

    def _consume_synchronous(
        self,
        plan: QueryPlan,
        subjects: Iterable[QueryEvaluationSubject],
        context: QueryEvaluationContext,
        token: CancellationToken | None,
    ) -> QueryEvaluationResult:
        approved: list[_ApprovedSubject] = []
        matches: list[QueryMatchResult] = []
        errors: list[str] = []
        for raw_subject in subjects:
            self._check_cancelled(token)
            if len(matches) >= self._policy.max_subjects:
                raise QueryEvaluationLimitError(
                    f"subject limit {self._policy.max_subjects} exceeded"
                )
            subject = self._validate_subject(raw_subject, len(matches))
            item = self._evaluate_one(plan, subject, context, matches, errors)
            if item is not None:
                approved.append(item)
        self._log("received", plan.query_id, {"total_received": len(matches)})
        return self._finalize(plan, context, approved, matches, errors)

    def _evaluate_one(
        self,
        plan: QueryPlan,
        subject: QueryEvaluationSubject,
        context: QueryEvaluationContext,
        matches: list[QueryMatchResult],
        errors: list[str],
    ) -> _ApprovedSubject | None:
        try:
            match = self._match(plan, subject, context)
        except QueryEvaluationError as error:
            if (
                self._policy.evaluation_error is EvaluationErrorBehavior.RAISE
                or not self._policy.allow_partial_evaluation
            ):
                raise
            identity = subject.logical_identity or f"subject-{len(matches)}"
            message = f"{type(error).__name__}: {error}"
            errors.append(message)
            match = QueryMatchResult(
                logical_identity=identity,
                matched=False,
                evaluated_filters=0,
                approved_filters=0,
                rejected_filters=0,
                missing_attributes=(),
                controlled_errors=(message,),
                justifications=("controlled error rejected subject",),
                predicate_records=(),
                timestamp=context.timestamp,
            )
        matches.append(match)
        if not match.matched:
            return None
        projection = (
            self._projection.project(subject, plan.projections, match)
            if plan.projections
            else None
        )
        return _ApprovedSubject(subject, match, projection)

    def _finalize(
        self,
        plan: QueryPlan,
        context: QueryEvaluationContext,
        approved: list[_ApprovedSubject],
        matches: list[QueryMatchResult],
        errors: list[str],
    ) -> QueryEvaluationResult:
        ordered = self._ordering.order(approved, plan.ordering)
        paged, offset, limit = self._pagination.paginate(ordered, plan.pagination)
        self._log(
            "pagination_applied",
            plan.query_id,
            {
                "offset": offset,
                "limit": limit,
                "before": len(ordered),
                "after": len(paged),
            },
        )
        return QueryEvaluationResult(
            query_id=plan.query_id,
            plan=plan,
            matched_items=tuple(item.match.logical_identity for item in paged),
            projected_items=tuple(
                item.projection for item in paged if item.projection is not None
            ),
            evaluation_records=tuple(matches),
            total_received=len(matches),
            total_evaluated=len(matches),
            total_matched=len(approved),
            total_rejected=len(matches) - len(approved),
            total_returned=len(paged),
            applied_offset=offset,
            applied_limit=limit,
            warnings=(),
            controlled_errors=tuple(errors),
            timestamp=context.timestamp,
            logical_duration=sum(item.evaluated_filters for item in matches),
        )

    def _match(
        self,
        plan: QueryPlan,
        subject: QueryEvaluationSubject,
        context: QueryEvaluationContext,
    ) -> QueryMatchResult:
        records: list[PredicateEvaluationRecord] = []
        reasons: list[str] = []
        matched = True
        for index, expression in enumerate(plan.effective_filters):
            outcome = self._groups.evaluate(subject, expression)
            records.extend(outcome.records)
            reasons.extend(outcome.justifications)
            if not outcome.matched:
                matched = False
                reasons.append(f"top-level AND short-circuited after filter {index}")
                break
        missing = tuple(
            dict.fromkeys(item.attribute for item in records if not item.attribute_exists)
        )
        approved = sum(item.matched for item in records)
        identity = subject.logical_identity
        if identity is None:
            raise InvalidQueryEvaluationSubjectError(
                "subject does not declare a logical identity"
            )
        return QueryMatchResult(
            logical_identity=identity,
            matched=matched,
            evaluated_filters=len(records),
            approved_filters=approved,
            rejected_filters=len(records) - approved,
            missing_attributes=missing,
            controlled_errors=(),
            justifications=tuple(reasons) or ("all declared filters approved",),
            predicate_records=tuple(records),
            timestamp=context.timestamp,
        )

    def _validate_subject(
        self, subject: object, index: int
    ) -> QueryEvaluationSubject:
        if isinstance(subject, Mapping):
            subject = MappingQueryEvaluationSubject(subject)
        if not isinstance(subject, QueryEvaluationSubject):
            raise InvalidQueryEvaluationSubjectError(
                f"subject at index {index} does not implement the public contract"
            )
        identity = subject.logical_identity
        if self._policy.require_logical_identity and identity is None:
            raise InvalidQueryEvaluationSubjectError(
                f"subject at index {index} has no logical identity"
            )
        if identity is None:
            subject = MappingQueryEvaluationSubject(
                {"value": subject.source}, identity=f"subject-{index}"
            )
        return subject

    @staticmethod
    def _check_cancelled(token: CancellationToken | None) -> None:
        if token is None:
            return
        try:
            token.throw_if_cancelled()
        except DiscoveryCancelledError as error:
            raise QueryEvaluationCancelledError(str(error)) from error

    def _log(
        self,
        action: str,
        query_id: str,
        context: Mapping[str, object],
        *,
        level: str = "info",
    ) -> None:
        payload = {"query_id": query_id, **context}
        getattr(self._logger, level)(
            f"query evaluation {action.replace('_', ' ')}",
            extra={
                "event": f"discovery.query.evaluation.{action}",
                "context": payload,
            },
        )

    def _log_completion(self, result: QueryEvaluationResult) -> None:
        self._log(
            "completed",
            result.query_id,
            {
                "total_evaluated": result.total_evaluated,
                "total_matched": result.total_matched,
                "total_rejected": result.total_rejected,
                "total_returned": result.total_returned,
            },
        )


class DefaultQueryEvaluationStream:
    """Public incremental façade over the canonical evaluation engine."""

    def __init__(self, engine: QueryEvaluationEngine | None = None) -> None:
        """Create a stream using an injectable canonical engine."""
        self._engine = engine or QueryEvaluationEngine()

    def evaluate(
        self,
        plan: QueryPlan,
        subjects: Iterable[QueryEvaluationSubject],
        *,
        cancellation_token: CancellationToken | None = None,
    ) -> QueryEvaluationResult:
        """Incrementally consume and synchronously evaluate subjects."""
        return self._engine.evaluate(
            plan, subjects, cancellation_token=cancellation_token
        )

    async def evaluate_async(
        self,
        plan: QueryPlan,
        subjects: AsyncIterable[QueryEvaluationSubject],
        *,
        cancellation_token: CancellationToken | None = None,
    ) -> QueryEvaluationResult:
        """Incrementally consume and asynchronously evaluate subjects."""
        return await self._engine.evaluate_async(
            plan, subjects, cancellation_token=cancellation_token
        )


__all__ = [
    "DefaultAttributeResolver",
    "DefaultQueryEvaluationStream",
    "FilterGroupEvaluator",
    "QueryEvaluationEngine",
    "QueryOrderingEngine",
    "QueryPaginationEngine",
    "QueryPredicateEvaluator",
    "QueryProjectionEngine",
]
