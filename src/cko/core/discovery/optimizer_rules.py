"""Canonical, semantics-preserving logical query optimization rules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import replace
from typing import ClassVar

from .optimizer_models import OptimizationCategory, OptimizationContext
from .query_models import (
    FilterGroup,
    FilterGroupOperator,
    QueryExpression,
    QueryFilter,
    QueryOperator,
    QueryOrdering,
    QueryPagination,
    QueryPlan,
)


def _key(expression: QueryExpression) -> str:
    return expression.to_json()


def _map_expression(
    expression: QueryExpression,
    transform: "ExpressionTransform",
) -> QueryExpression:
    if isinstance(expression, QueryFilter):
        return transform(expression)
    mapped = FilterGroup(
        expression.operator,
        tuple(_map_expression(item, transform) for item in expression.filters),
    )
    return transform(mapped)


class ExpressionTransform:
    """Callable protocol substitute kept dependency-free for Python runtime use."""

    def __call__(self, expression: QueryExpression) -> QueryExpression:
        """Transform one canonical expression."""
        return expression


def _rewrite(
    plan: QueryPlan,
    transform: ExpressionTransform,
) -> QueryPlan:
    return replace(
        plan,
        effective_filters=tuple(
            _map_expression(item, transform) for item in plan.effective_filters
        ),
    )


class OptimizationRule(ABC):
    """Abstract deterministic transformation over an immutable query plan."""

    id: ClassVar[str]
    name: ClassVar[str]
    description: ClassVar[str]
    priority: ClassVar[int]
    category: ClassVar[OptimizationCategory]
    version: ClassVar[str] = "1.0"
    deterministic: ClassVar[bool] = True

    def __init__(self, *, enabled: bool = True) -> None:
        """Create a rule with an explicit activation flag."""
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be boolean")
        self.enabled = enabled

    @abstractmethod
    def apply(self, context: OptimizationContext) -> QueryPlan:
        """Return a semantically equivalent plan for the supplied context."""


class PredicateSimplificationRule(OptimizationRule):
    """Collapse redundant unary boolean wrappers and double negation."""

    id = "predicate_simplification"
    name = "Predicate Simplification"
    description = "Collapses unary AND/OR groups and double NOT groups."
    priority = 10
    category = OptimizationCategory.PREDICATE

    def apply(self, context: OptimizationContext) -> QueryPlan:
        """Simplify recursively without changing predicate truth values."""
        class Simplify(ExpressionTransform):
            def __call__(self, expression: QueryExpression) -> QueryExpression:
                if not isinstance(expression, FilterGroup):
                    return expression
                if expression.operator in {
                    FilterGroupOperator.AND, FilterGroupOperator.OR,
                } and len(expression.filters) == 1:
                    return expression.filters[0]
                nested = expression.filters[0]
                if (expression.operator is FilterGroupOperator.NOT
                        and isinstance(nested, FilterGroup)
                        and nested.operator is FilterGroupOperator.NOT):
                    return nested.filters[0]
                return expression

        previous = context.current_plan
        while True:
            current = _rewrite(previous, Simplify())
            if current == previous:
                return current
            previous = current


class BooleanNormalizationRule(OptimizationRule):
    """Flatten and deterministically order associative boolean groups."""

    id = "boolean_normalization"
    name = "Boolean Normalization"
    description = "Flattens associative groups and orders commutative members."
    priority = 20
    category = OptimizationCategory.BOOLEAN

    def apply(self, context: OptimizationContext) -> QueryPlan:
        """Normalize AND and OR trees into a stable logical representation."""
        class Normalize(ExpressionTransform):
            def __call__(self, expression: QueryExpression) -> QueryExpression:
                if not isinstance(expression, FilterGroup):
                    return expression
                if expression.operator is FilterGroupOperator.NOT:
                    return expression
                members: list[QueryExpression] = []
                for item in expression.filters:
                    if (isinstance(item, FilterGroup)
                            and item.operator is expression.operator):
                        members.extend(item.filters)
                    else:
                        members.append(item)
                return FilterGroup(expression.operator,
                                   tuple(sorted(members, key=_key)))

        plan = _rewrite(context.current_plan, Normalize())
        return replace(plan, effective_filters=tuple(
            sorted(plan.effective_filters, key=_key)
        ))


class RedundantFilterRemovalRule(OptimizationRule):
    """Remove repeated predicates from conjunctions and disjunctions."""

    id = "redundant_filter_removal"
    name = "Redundant Filter Removal"
    description = "Removes logically idempotent duplicate filter expressions."
    priority = 30
    category = OptimizationCategory.PREDICATE

    def apply(self, context: OptimizationContext) -> QueryPlan:
        """Remove exact duplicates while preserving the first occurrence."""
        class Deduplicate(ExpressionTransform):
            def __call__(self, expression: QueryExpression) -> QueryExpression:
                if not isinstance(expression, FilterGroup):
                    return expression
                if expression.operator is FilterGroupOperator.NOT:
                    return expression
                seen: set[str] = set()
                members = []
                for item in expression.filters:
                    fingerprint = _key(item)
                    if fingerprint not in seen:
                        members.append(item)
                        seen.add(fingerprint)
                return FilterGroup(expression.operator, tuple(members))

        plan = _rewrite(context.current_plan, Deduplicate())
        seen: set[str] = set()
        filters = []
        for item in plan.effective_filters:
            fingerprint = _key(item)
            if fingerprint not in seen:
                filters.append(item)
                seen.add(fingerprint)
        return replace(plan, effective_filters=tuple(filters))


class DuplicateProjectionRemovalRule(OptimizationRule):
    """Remove duplicate projected attributes without changing their values."""

    id = "duplicate_projection_removal"
    name = "Duplicate Projection Removal"
    description = "Keeps the first projection for every logical attribute."
    priority = 40
    category = OptimizationCategory.PROJECTION

    def apply(self, context: OptimizationContext) -> QueryPlan:
        """Deduplicate projections in stable input order."""
        seen: set[str] = set()
        projections = []
        for item in context.current_plan.projections:
            if item.attribute not in seen:
                projections.append(item)
                seen.add(item.attribute)
        return replace(context.current_plan, projections=tuple(projections))


class ProjectionNormalizationRule(OptimizationRule):
    """Order distinct projections by their canonical attribute name."""

    id = "projection_normalization"
    name = "Projection Normalization"
    description = "Produces deterministic canonical projection ordering."
    priority = 50
    category = OptimizationCategory.PROJECTION

    def apply(self, context: OptimizationContext) -> QueryPlan:
        """Sort projections without changing the projected attribute set."""
        projections = tuple(sorted(
            context.current_plan.projections, key=lambda item: item.attribute
        ))
        return replace(context.current_plan, projections=projections)


class ConstantExpressionRule(OptimizationRule):
    """Reduce singleton membership operations to scalar comparisons."""

    id = "constant_expression"
    name = "Constant Expression"
    description = "Rewrites singleton IN and NOT IN predicates exactly."
    priority = 60
    category = OptimizationCategory.EXPRESSION

    def apply(self, context: OptimizationContext) -> QueryPlan:
        """Replace singleton membership with its equivalent scalar operator."""
        class Fold(ExpressionTransform):
            def __call__(self, expression: QueryExpression) -> QueryExpression:
                if not isinstance(expression, QueryFilter):
                    return expression
                if expression.operator is QueryOperator.IN and len(
                    expression.value
                ) == 1:
                    return QueryFilter(
                        expression.attribute, QueryOperator.EQUALS,
                        expression.value[0],
                    )
                if expression.operator is QueryOperator.NOT_IN and len(
                    expression.value
                ) == 1:
                    return QueryFilter(
                        expression.attribute, QueryOperator.NOT_EQUALS,
                        expression.value[0],
                    )
                return expression

        return _rewrite(context.current_plan, Fold())


class SortNormalizationRule(OptimizationRule):
    """Normalize sort priorities and remove exact duplicate declarations."""

    id = "sort_normalization"
    name = "Sort Normalization"
    description = "Renumbers canonical sort priorities without reordering keys."
    priority = 70
    category = OptimizationCategory.ORDERING

    def apply(self, context: OptimizationContext) -> QueryPlan:
        """Produce contiguous priorities for the existing ordered clauses."""
        seen: set[tuple[str, object]] = set()
        ordering = []
        for item in context.current_plan.ordering:
            identity = (item.attribute, item.direction)
            if identity not in seen:
                ordering.append(item)
                seen.add(identity)
        normalized = tuple(
            QueryOrdering(item.attribute, item.direction, priority)
            for priority, item in enumerate(ordering)
        )
        return replace(context.current_plan, ordering=normalized)


class LimitNormalizationRule(OptimizationRule):
    """Normalize page pagination to its equivalent offset/limit boundary."""

    id = "limit_normalization"
    name = "Limit Normalization"
    description = "Canonicalizes pagination as offset and limit."
    priority = 80
    category = OptimizationCategory.PAGINATION

    def apply(self, context: OptimizationContext) -> QueryPlan:
        """Convert page boundaries without changing the selected result slice."""
        pagination = context.current_plan.pagination
        if pagination is None:
            return context.current_plan
        if pagination.page is None:
            normalized = QueryPagination(
                offset=pagination.offset or 0, limit=pagination.limit
            )
        else:
            offset = (pagination.page - 1) * pagination.page_size
            normalized = QueryPagination(
                offset=offset, limit=pagination.limit or pagination.page_size
            )
        return replace(context.current_plan, pagination=normalized)


class EmptyPredicateRule(OptimizationRule):
    """Guard the canonical empty-filter identity without inventing predicates."""

    id = "empty_predicate"
    name = "Empty Predicate"
    description = "Preserves an empty top-level predicate set as logical TRUE."
    priority = 90
    category = OptimizationCategory.SAFETY

    def apply(self, context: OptimizationContext) -> QueryPlan:
        """Preserve the canonical empty predicate representation unchanged."""
        return context.current_plan


class IdentityTransformationRule(OptimizationRule):
    """Explicit identity rule used to audit fixed-point behavior."""

    id = "identity_transformation"
    name = "Identity Transformation"
    description = "Returns the current immutable query plan unchanged."
    priority = 100
    category = OptimizationCategory.SAFETY

    def apply(self, context: OptimizationContext) -> QueryPlan:
        """Return the current plan exactly."""
        return context.current_plan


CANONICAL_OPTIMIZATION_RULES = (
    PredicateSimplificationRule,
    BooleanNormalizationRule,
    RedundantFilterRemovalRule,
    DuplicateProjectionRemovalRule,
    ProjectionNormalizationRule,
    ConstantExpressionRule,
    SortNormalizationRule,
    LimitNormalizationRule,
    EmptyPredicateRule,
    IdentityTransformationRule,
)


__all__ = [
    "BooleanNormalizationRule", "CANONICAL_OPTIMIZATION_RULES",
    "ConstantExpressionRule", "DuplicateProjectionRemovalRule",
    "EmptyPredicateRule", "IdentityTransformationRule",
    "LimitNormalizationRule", "OptimizationRule",
    "PredicateSimplificationRule", "ProjectionNormalizationRule",
    "RedundantFilterRemovalRule", "SortNormalizationRule",
]
