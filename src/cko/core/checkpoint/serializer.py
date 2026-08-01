"""Default deterministic checkpoint serializer."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Mapping

from .contracts import CheckpointSerializer
from .errors import (
    CheckpointException,
    CheckpointIntegrityError,
    CheckpointSerializationError,
)
from .models import CheckpointRecord


_LOGGER = logging.getLogger("cko.core.checkpoint.serializer")


class DefaultCheckpointSerializer(CheckpointSerializer):
    """Serialize checkpoint records as strict canonical JSON."""

    def serialize(self, record: CheckpointRecord) -> bytes:
        """Serialize a record to canonical UTF-8 bytes."""
        if not isinstance(record, CheckpointRecord):
            raise CheckpointSerializationError(
                "record must be CheckpointRecord"
            )
        try:
            payload = json.dumps(
                record.to_dict(),
                allow_nan=False,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        except (TypeError, ValueError, UnicodeError) as error:
            raise CheckpointSerializationError(
                "checkpoint record serialization failed"
            ) from error
        _LOGGER.info(
            "checkpoint_serialized",
            extra={
                "event": "checkpoint_serialized",
                "context": {
                    "checkpoint_id": record.identifier.checkpoint_id,
                    "size": len(payload),
                },
            },
        )
        return payload

    def deserialize(self, payload: bytes) -> CheckpointRecord:
        """Deserialize strict UTF-8 JSON and validate full integrity."""
        if not isinstance(payload, bytes):
            raise CheckpointSerializationError("payload must be bytes")
        try:
            text = payload.decode("utf-8")
            decoded = json.loads(
                text,
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError(value)
                ),
            )
        except (
            UnicodeDecodeError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            raise CheckpointSerializationError(
                "checkpoint payload is not valid strict UTF-8 JSON"
            ) from error
        if not isinstance(decoded, Mapping):
            raise CheckpointSerializationError(
                "checkpoint payload must contain a JSON object"
            )
        try:
            record = CheckpointRecord.from_dict(decoded)
        except CheckpointIntegrityError:
            _LOGGER.error(
                "checkpoint_integrity_failed",
                extra={"event": "checkpoint_integrity_failed", "context": {}},
            )
            raise
        except CheckpointException as error:
            raise CheckpointSerializationError(
                "checkpoint record deserialization failed"
            ) from error
        canonical = self.serialize(record)
        if canonical != payload:
            raise CheckpointSerializationError(
                "checkpoint payload is not in canonical JSON form"
            )
        return record

    def digest(self, record: CheckpointRecord) -> str:
        """Calculate SHA-256 over canonical serialized record bytes."""
        return hashlib.sha256(self.serialize(record)).hexdigest()


__all__ = ["DefaultCheckpointSerializer"]
