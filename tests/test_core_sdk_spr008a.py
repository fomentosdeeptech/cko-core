"""Validação unitária da fundação canônica criada na SPR-008A."""

from __future__ import annotations

import io
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from cko.core.config import SDKConfig, load_config
from cko.core.contracts import Clock, EventPublisher, Plugin, Repository
from cko.core.exceptions import ConfigurationError
from cko.core.identity import CanonicalId, Origin, SemanticVersion
from cko.core.logging import configure_logging
from cko.core.metadata import UniversalMetadata
from cko.core.models import (
    CanonicalDocument,
    CanonicalEvent,
    DocumentLocation,
    InventoryItem,
)
from cko.core.utils import utc_now


NOW = datetime(2026, 7, 14, 12, 0, tzinfo=UTC)


def _document() -> CanonicalDocument:
    document_id = CanonicalId.new()
    return CanonicalDocument(
        id=document_id,
        version=SemanticVersion.parse("1.0.0"),
        origin=Origin("unit-test", NOW, "fixture-1"),
        metadata=UniversalMetadata(
            media_type="text/plain",
            created_at=NOW,
            modified_at=NOW,
            language="pt-BR",
            attributes={"sha256": "a" * 64},
        ),
        title="Documento canônico",
    )


def test_all_public_packages_import() -> None:
    import cko.core.config
    import cko.core.contracts
    import cko.core.exceptions
    import cko.core.identity
    import cko.core.logging
    import cko.core.metadata
    import cko.core.models
    import cko.core.utils

    assert cko.core.contracts.Repository is Repository


def test_constructs_canonical_models() -> None:
    document = _document()
    location = DocumentLocation(
        id=CanonicalId.new(),
        document_id=document.id,
        uri="file:///acervo/documento.txt",
        observed_at=NOW,
    )
    item = InventoryItem(CanonicalId.new(), document, location, NOW)

    assert item.location.document_id == item.document.id
    assert str(document.version) == "1.0.0"
    assert document.metadata.attributes["sha256"] == "a" * 64


def test_models_reject_inconsistent_or_naive_data() -> None:
    document = _document()
    wrong_location = DocumentLocation(
        id=CanonicalId.new(),
        document_id=CanonicalId.new(),
        uri="https://example.invalid/document",
        observed_at=NOW,
    )
    with pytest.raises(ValueError, match="document_id"):
        InventoryItem(CanonicalId.new(), document, wrong_location, NOW)
    with pytest.raises(ValueError, match="fuso horário"):
        Origin("unit-test", datetime(2026, 7, 14))


def test_semantic_version_precedence() -> None:
    assert SemanticVersion.parse("1.0.0-alpha.1") < SemanticVersion.parse("1.0.0")
    assert SemanticVersion.parse("1.2.0") > SemanticVersion.parse("1.1.9")


class _MemoryRepository:
    def __init__(self, document: CanonicalDocument) -> None:
        self.document = document

    def get(self, entity_id: CanonicalId) -> CanonicalDocument | None:
        return self.document if self.document.id == entity_id else None

    def contains(self, entity_id: CanonicalId) -> bool:
        return self.get(entity_id) is not None


class _FixedClock:
    def now(self) -> datetime:
        return NOW


class _MemoryPublisher:
    def __init__(self) -> None:
        self.events: list[CanonicalEvent] = []

    def publish(self, event: CanonicalEvent) -> None:
        self.events.append(event)


class _Plugin:
    name = "fixture"
    version = SemanticVersion.parse("1.0.0")

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None


def test_contracts_are_structural_and_runtime_checkable() -> None:
    document = _document()
    assert isinstance(_MemoryRepository(document), Repository)
    assert isinstance(_FixedClock(), Clock)
    assert isinstance(_MemoryPublisher(), EventPublisher)
    assert isinstance(_Plugin(), Plugin)


def test_loads_toml_and_environment_override() -> None:
    config_file = Path(__file__).parent / "fixtures" / "spr008a_config.toml"
    config = load_config(
        config_file,
        environ={"CKO_LOG_LEVEL": "DEBUG", "CKO_VALUE_REGION": "br"},
    )

    assert config == SDKConfig(
        environment="test",
        log_level="DEBUG",
        service_name="fixture",
        values={"timeout_seconds": 15, "region": "br"},
    )


def test_rejects_invalid_configuration() -> None:
    config_file = Path(__file__).parent / "fixtures" / "spr008a_config.yaml"
    with pytest.raises(ConfigurationError, match="formato suportado"):
        load_config(config_file, environ={})


def test_structured_logging_emits_json() -> None:
    stream = io.StringIO()
    logger = configure_logging(stream=stream, logger_name="cko.test")
    logger.info("modelo criado", extra={"event": "model.created", "context": {"id": 1}})
    payload = json.loads(stream.getvalue())

    assert payload["event"] == "model.created"
    assert payload["context"] == {"id": 1}
    assert payload["level"] == "INFO"


def test_utc_now_is_timezone_aware() -> None:
    assert utc_now().utcoffset() is not None
