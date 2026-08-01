"""Default invariant validation for Discovery contracts."""

from __future__ import annotations

from .contracts import DiscoverySource
from .errors import (
    DiscoveryValidationError,
    InvalidDiscoveredItemError,
    InvalidDiscoveryRequestError,
    InvalidDiscoverySourceError,
)
from .models import (
    DiscoveredItem,
    DiscoveryCapability,
    DiscoveryRequest,
    DiscoveryResult,
    DiscoveryStatus,
)
from .policies import ensure_supported_capabilities, validate_policy


class DefaultDiscoveryValidator:
    """Validate canonical invariants without consulting infrastructure."""

    def validate_source(self, source: DiscoverySource) -> None:
        """Validate stable identity and declared capabilities."""
        try:
            source_id = source.id
            capabilities = frozenset(source.capabilities)
        except (AttributeError, TypeError, ValueError) as error:
            raise InvalidDiscoverySourceError("invalid discovery source") from error
        if (
            str(source_id).strip() == ""
            or len(capabilities) != len(source.capabilities)
            or any(
                not isinstance(capability, DiscoveryCapability)
                for capability in capabilities
            )
        ):
            raise InvalidDiscoverySourceError("invalid source identity or capabilities")

    def validate_request(
        self,
        source: DiscoverySource,
        request: DiscoveryRequest,
    ) -> None:
        """Validate request identity, policy and required capabilities."""
        self.validate_source(source)
        if request.source_id != source.id:
            raise InvalidDiscoveryRequestError("request source_id differs from source")
        try:
            validate_policy(request.policy)
            ensure_supported_capabilities(
                request.required_capabilities,
                source.capabilities,
            )
        except ValueError as error:
            raise InvalidDiscoveryRequestError(str(error)) from error

    def validate_item(
        self,
        request: DiscoveryRequest,
        item: DiscoveredItem,
    ) -> None:
        """Validate provenance and correlation of one observation."""
        if item.source_id != request.source_id:
            raise InvalidDiscoveredItemError("item source differs from request")
        if item.correlation_id != request.context.correlation_id:
            raise InvalidDiscoveredItemError("item correlation differs from request")

    def validate_result(
        self,
        request: DiscoveryRequest,
        result: DiscoveryResult,
    ) -> None:
        """Validate result identity, counts, state and all observations."""
        if result.request_id != request.id or result.source_id != request.source_id:
            raise DiscoveryValidationError("result identity differs from request")
        for item in result.items:
            self.validate_item(request, item)
        if result.metrics.observed_count != (
            len(result.items) + result.metrics.rejected_count
        ):
            raise DiscoveryValidationError("result metrics do not match observations")
        if result.metrics.accepted_count != len(result.items):
            raise DiscoveryValidationError("accepted_count differs from result items")
        if result.metrics.warning_count != len(result.warnings):
            raise DiscoveryValidationError("warning_count differs from warnings")
        if result.metrics.error_count != len(result.errors):
            raise DiscoveryValidationError("error_count differs from errors")
        if (
            result.status is DiscoveryStatus.COMPLETED_WITH_WARNINGS
            and not result.warnings
        ):
            raise DiscoveryValidationError("warning status requires warnings")
        if result.status is DiscoveryStatus.COMPLETED and result.warnings:
            raise DiscoveryValidationError("completed result cannot contain warnings")


__all__ = ["DefaultDiscoveryValidator"]
