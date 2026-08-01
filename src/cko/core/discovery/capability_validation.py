"""Validation and automatic resolution for Discovery capabilities."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from cko.core.utils import utc_now

from .capability_errors import (
    CapabilityConflictError,
    CapabilityDependencyError,
    CapabilityValidationError,
)
from .capability_models import (
    Capability,
    CapabilityReport,
    CapabilityRequirement,
    CapabilityRequirementType,
    CapabilitySet,
)


class CapabilityValidationEngine:
    """Validate requirements, dependencies, conflicts and versions."""

    def validate(
        self,
        capabilities: CapabilitySet,
        requirements: Iterable[CapabilityRequirement] = (),
        *,
        timestamp: datetime | None = None,
    ) -> CapabilityReport:
        """Return an immutable audit report without mutating the input set."""
        if not isinstance(capabilities, CapabilitySet):
            raise CapabilityValidationError(
                "capabilities must be CapabilitySet"
            )
        declared = tuple(requirements)
        if any(not isinstance(item, CapabilityRequirement) for item in declared):
            raise CapabilityValidationError(
                "requirements must contain CapabilityRequirement"
            )
        missing: dict[tuple[str, str], CapabilityRequirement] = {}
        rejected_ids: set[str] = set()
        conflicting_ids: set[str] = set()
        reasons: dict[str, list[str]] = {}

        def explain(key: str, message: str) -> None:
            reasons.setdefault(key, []).append(message)

        for requirement in sorted(
            declared,
            key=lambda item: (
                item.capability_id,
                item.requirement_type.value,
                str(item.minimum_version),
            ),
        ):
            candidate = capabilities.get(requirement.capability_id)
            if requirement.is_satisfied_by(candidate):
                if candidate is not None:
                    explain(candidate.id, "declared requirement satisfied")
                continue
            if requirement.requirement_type is CapabilityRequirementType.PROHIBITED:
                if candidate is not None:
                    conflicting_ids.add(candidate.id)
                    rejected_ids.add(candidate.id)
                    explain(candidate.id, "prohibited capability is present")
                continue
            key = (requirement.capability_id, requirement.to_json())
            missing[key] = requirement
            explain(
                requirement.capability_id,
                self._requirement_failure(requirement, candidate),
            )

        for capability in capabilities:
            for dependency in capability.dependencies:
                candidate = capabilities.get(dependency.capability_id)
                if dependency.is_satisfied_by(candidate):
                    if candidate is not None:
                        explain(
                            capability.id,
                            f"dependency {candidate.id} satisfied",
                        )
                    continue
                if dependency.requirement_type is CapabilityRequirementType.OPTIONAL:
                    explain(
                        capability.id,
                        f"optional dependency {dependency.capability_id} unavailable",
                    )
                    continue
                key = (dependency.capability_id, dependency.to_json())
                missing[key] = dependency
                rejected_ids.add(capability.id)
                explain(
                    capability.id,
                    self._requirement_failure(dependency, candidate),
                )
            for incompatibility in capability.incompatibilities:
                candidate = capabilities.get(incompatibility.capability_id)
                if incompatibility.is_satisfied_by(candidate):
                    continue
                conflicting_ids.add(capability.id)
                rejected_ids.add(capability.id)
                if candidate is not None:
                    conflicting_ids.add(candidate.id)
                    rejected_ids.add(candidate.id)
                explain(
                    capability.id,
                    f"conflicts with {incompatibility.capability_id}",
                )

        accepted = CapabilitySet.of(
            item for item in capabilities if item.id not in rejected_ids
        )
        rejected = CapabilitySet.of(
            item for item in capabilities if item.id in rejected_ids
        )
        conflicting = CapabilitySet.of(
            item for item in capabilities if item.id in conflicting_ids
        )
        for item in accepted:
            reasons.setdefault(item.id, ["capability accepted"])
        return CapabilityReport(
            accepted=accepted,
            rejected=rejected,
            missing=tuple(
                missing[key]
                for key in sorted(missing, key=lambda item: item)
            ),
            conflicting=conflicting,
            justifications={
                key: tuple(dict.fromkeys(values))
                for key, values in sorted(reasons.items())
            },
            timestamp=timestamp or utc_now(),
        )

    def ensure_valid(
        self,
        capabilities: CapabilitySet,
        requirements: Iterable[CapabilityRequirement] = (),
    ) -> CapabilitySet:
        """Return the accepted set or raise the most specific public error."""
        report = self.validate(capabilities, requirements)
        if report.conflicting:
            identifiers = ", ".join(item.id for item in report.conflicting)
            raise CapabilityConflictError(
                f"capability conflicts detected: {identifiers}"
            )
        if report.missing:
            identifiers = ", ".join(
                sorted({item.capability_id for item in report.missing})
            )
            raise CapabilityDependencyError(
                f"capability requirements are unsatisfied: {identifiers}"
            )
        if report.rejected:
            raise CapabilityValidationError("capability set was rejected")
        return report.accepted

    @staticmethod
    def _requirement_failure(
        requirement: CapabilityRequirement,
        candidate: Capability | None,
    ) -> str:
        """Build a stable explanation for an unsatisfied requirement."""
        if candidate is None:
            return "required capability is absent"
        if (
            requirement.minimum_version is not None
            and candidate.version < requirement.minimum_version
        ):
            return (
                f"version {candidate.version} is below minimum "
                f"{requirement.minimum_version}"
            )
        if candidate.version in requirement.incompatible_versions:
            return f"version {candidate.version} is explicitly incompatible"
        return "capability requirement is unsatisfied"


class CapabilityResolver:
    """Resolve a valid final set by expanding declared dependencies."""

    def __init__(
        self,
        validator: CapabilityValidationEngine | None = None,
    ) -> None:
        """Create a resolver with an injectable pure validation engine."""
        self._validator = validator or CapabilityValidationEngine()

    def resolve(
        self,
        requested: CapabilitySet,
        available: CapabilitySet,
        requirements: Iterable[CapabilityRequirement] = (),
    ) -> CapabilitySet:
        """Expand dependencies deterministically and return a valid set."""
        if not isinstance(requested, CapabilitySet):
            raise CapabilityValidationError("requested must be CapabilitySet")
        if not isinstance(available, CapabilitySet):
            raise CapabilityValidationError("available must be CapabilitySet")
        selected: dict[str, Capability] = {
            item.id: item for item in requested
        }
        pending = sorted(selected)
        processed: set[str] = set()
        while pending:
            capability_id = pending.pop(0)
            if capability_id in processed:
                continue
            processed.add(capability_id)
            capability = selected[capability_id]
            for dependency in capability.dependencies:
                candidate = available.get(dependency.capability_id)
                if candidate is None:
                    if dependency.requirement_type is CapabilityRequirementType.OPTIONAL:
                        continue
                    raise CapabilityDependencyError(
                        f"dependency {dependency.capability_id!r} is unavailable"
                    )
                if not dependency.is_satisfied_by(candidate):
                    if dependency.requirement_type is CapabilityRequirementType.OPTIONAL:
                        continue
                    raise CapabilityDependencyError(
                        f"dependency {dependency.capability_id!r} has an "
                        "unsupported version"
                    )
                current = selected.get(candidate.id)
                if current is not None and current != candidate:
                    raise CapabilityDependencyError(
                        f"dependency {candidate.id!r} has divergent declarations"
                    )
                if current is None:
                    selected[candidate.id] = candidate
                    pending.append(candidate.id)
                    pending.sort()
        resolved = CapabilitySet.of(selected.values())
        return self._validator.ensure_valid(resolved, requirements)


__all__ = ["CapabilityResolver", "CapabilityValidationEngine"]
