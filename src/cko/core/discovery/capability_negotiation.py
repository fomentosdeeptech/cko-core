"""Deterministic capability negotiation across Discovery participants."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Sequence

from cko.core.logging import get_logger
from cko.core.utils import utc_now

from .capability_errors import CapabilityNegotiationError
from .capability_models import (
    Capability,
    CapabilityReport,
    CapabilityRequirement,
    CapabilitySet,
)
from .capability_validation import CapabilityValidationEngine


class CapabilityNegotiationEngine:
    """Negotiate the common capabilities of the four SDK participant roles."""

    def __init__(
        self,
        validator: CapabilityValidationEngine | None = None,
    ) -> None:
        """Create an infrastructure-free negotiator."""
        self._validator = validator or CapabilityValidationEngine()
        self._logger = get_logger("core.discovery.capability")

    def negotiate(
        self,
        provider: CapabilitySet,
        pipeline: CapabilitySet,
        executor: CapabilitySet,
        consumer: CapabilitySet,
        requirements: Iterable[CapabilityRequirement] = (),
        *,
        timestamp: datetime | None = None,
    ) -> CapabilityReport:
        """Return the deterministic common-set negotiation report."""
        participants = {
            "provider": provider,
            "pipeline": pipeline,
            "executor": executor,
            "consumer": consumer,
        }
        if any(not isinstance(item, CapabilitySet) for item in participants.values()):
            raise CapabilityNegotiationError(
                "all negotiation participants must declare CapabilitySet"
            )
        declared_requirements = tuple(requirements)
        if any(
            not isinstance(item, CapabilityRequirement)
            for item in declared_requirements
        ):
            raise CapabilityNegotiationError(
                "requirements must contain CapabilityRequirement"
            )
        all_ids = sorted(
            {
                capability.id
                for capability_set in participants.values()
                for capability in capability_set
            }
        )
        self._logger.info(
            "capability negotiation started",
            extra={
                "event": "discovery.capability.negotiation.started",
                "context": {
                    "participant_count": len(participants),
                    "declared_capability_count": len(all_ids),
                    "requirement_count": len(declared_requirements),
                },
            },
        )
        common: list[Capability] = []
        rejected: list[Capability] = []
        negotiation_reasons: dict[str, Sequence[str]] = {}
        for capability_id in all_ids:
            declarations = {
                role: capability_set.get(capability_id)
                for role, capability_set in participants.items()
            }
            present = [
                item for item in declarations.values() if item is not None
            ]
            if len(present) == len(participants):
                selected = min(
                    present,
                    key=lambda item: (item.version, item.to_json()),
                )
                common.append(selected)
                negotiation_reasons[capability_id] = (
                    "supported by provider, pipeline, executor and consumer",
                    f"negotiated semantic version {selected.version}",
                )
            else:
                representative = max(
                    present,
                    key=lambda item: (item.version, item.to_json()),
                )
                rejected.append(representative)
                absent = ", ".join(
                    role
                    for role, declaration in declarations.items()
                    if declaration is None
                )
                negotiation_reasons[capability_id] = (
                    f"not supported by participant roles: {absent}",
                )
        instant = timestamp or utc_now()
        validation = self._validator.validate(
            CapabilitySet.of(common),
            declared_requirements,
            timestamp=instant,
        )
        rejected_by_id = {item.id: item for item in rejected}
        rejected_by_id.update({item.id: item for item in validation.rejected})
        justifications = dict(negotiation_reasons)
        for key, values in validation.justifications.items():
            justifications[key] = tuple(
                dict.fromkeys(justifications.get(key, ()) + values)
            )
        report = CapabilityReport(
            accepted=validation.accepted,
            rejected=CapabilitySet.of(rejected_by_id.values()),
            missing=validation.missing,
            conflicting=validation.conflicting,
            justifications=justifications,
            timestamp=instant,
        )
        self._logger.info(
            "capability negotiation completed",
            extra={
                "event": "discovery.capability.negotiation.completed",
                "context": {
                    "accepted_count": len(report.accepted),
                    "rejected_count": len(report.rejected),
                    "missing_count": len(report.missing),
                    "conflicting_count": len(report.conflicting),
                    "valid": report.is_valid,
                },
            },
        )
        return report


__all__ = ["CapabilityNegotiationEngine"]
