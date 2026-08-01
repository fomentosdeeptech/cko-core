"""Infrastructure-free orchestration of the Discovery contracts."""

from __future__ import annotations

from cko.core.contracts import Clock
from cko.core.logging import get_logger
from cko.core.models import Asset

from .contracts import (
    DiscoveryAssetMapper,
    DiscoveryEventPublisher,
    DiscoveryProvider,
    DiscoverySource,
    DiscoveryValidator,
)
from .errors import DiscoveryProviderError
from .events import (
    DISCOVERY_BATCH_COMPLETED,
    DISCOVERY_CANCELLED,
    DISCOVERY_COMPLETED,
    DISCOVERY_FAILED,
    DISCOVERY_ITEM_OBSERVED,
    DISCOVERY_STARTED,
    create_discovery_event,
)
from .models import DiscoveryRequest, DiscoveryResult, DiscoveryStatus


class DiscoveryService:
    """Coordinate ports and models without accessing external infrastructure."""

    def __init__(
        self,
        validator: DiscoveryValidator,
        publisher: DiscoveryEventPublisher,
        clock: Clock,
        mapper: DiscoveryAssetMapper | None = None,
    ) -> None:
        self._validator = validator
        self._publisher = publisher
        self._clock = clock
        self._mapper = mapper
        self._logger = get_logger("cko.core.discovery")

    def discover(
        self,
        source: DiscoverySource,
        provider: DiscoveryProvider,
        request: DiscoveryRequest,
    ) -> DiscoveryResult:
        """Execute and validate a provider, publishing stable lifecycle events."""
        self._validator.validate_request(source, request)
        self._publish(
            DISCOVERY_STARTED,
            request,
            {"request_id": str(request.id)},
        )
        self._logger.info(
            "discovery started",
            extra={"request_id": str(request.id), "source_id": str(source.id)},
        )
        try:
            result = provider.discover(source, request)
            if not isinstance(result, DiscoveryResult):
                raise TypeError("provider must return DiscoveryResult")
            self._validator.validate_result(request, result)
        except Exception as error:
            self._publish(
                DISCOVERY_FAILED,
                request,
                {"request_id": str(request.id), "error_type": type(error).__name__},
            )
            self._logger.error(
                "discovery failed",
                extra={
                    "request_id": str(request.id),
                    "error_type": type(error).__name__,
                },
            )
            if isinstance(error, DiscoveryProviderError):
                raise
            raise DiscoveryProviderError(
                "discovery provider execution failed"
            ) from error

        for item in result.items:
            self._publish(
                DISCOVERY_ITEM_OBSERVED,
                request,
                {
                    "request_id": str(request.id),
                    "external_reference": item.external_reference,
                },
            )
        for batch in result.batches:
            self._publish(
                DISCOVERY_BATCH_COMPLETED,
                request,
                {
                    "request_id": str(request.id),
                    "batch_id": str(batch.id),
                    "sequence": batch.sequence,
                },
            )
        terminal_event = {
            DiscoveryStatus.CANCELLED: DISCOVERY_CANCELLED,
            DiscoveryStatus.FAILED: DISCOVERY_FAILED,
        }.get(result.status, DISCOVERY_COMPLETED)
        self._publish(
            terminal_event,
            request,
            {"request_id": str(request.id), "status": result.status.value},
        )
        return result

    def map_assets(self, result: DiscoveryResult) -> tuple[Asset, ...]:
        """Explicitly map result items; never register them in an Inventory."""
        if self._mapper is None:
            raise ValueError("no discovery asset mapper was configured")
        return tuple(self._mapper.map_item(item) for item in result.items)

    def _publish(
        self,
        name: str,
        request: DiscoveryRequest,
        attributes: dict[str, object],
    ) -> None:
        event = create_discovery_event(
            name,
            self._clock.now(),
            request.source_id,
            attributes,
        )
        self._publisher.publish(event)


__all__ = ["DiscoveryService"]
