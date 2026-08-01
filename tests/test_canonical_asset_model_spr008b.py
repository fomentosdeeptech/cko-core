"""Testes unitários do Modelo Canônico de Ativos da SPR-008B."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime

import pytest

from cko.core import (
    Asset,
    AssetClassification,
    AssetFingerprint,
    AssetHash,
    AssetLifecycle,
    AssetRelation,
    AssetStatus,
    AudioAsset,
    CanonicalId,
    DatabaseAsset,
    DocumentAsset,
    FolderAsset,
    ImageAsset,
    KnowledgeAsset,
    ProjectAsset,
    ReferenceAsset,
    UniversalMetadata,
    VideoAsset,
    asset_from_dict,
)


NOW = datetime(2026, 7, 14, 18, 0, tzinfo=UTC)


def _metadata() -> UniversalMetadata:
    return UniversalMetadata(
        media_type="application/octet-stream",
        created_at=NOW,
        modified_at=NOW,
        language="pt-BR",
        attributes={"source": {"system": "unit-test"}, "labels": ["canonical"]},
    )


def _common(asset_id: CanonicalId | None = None) -> dict[str, object]:
    return {
        "id": asset_id or CanonicalId.new(),
        "name": "Ativo canônico",
        "metadata": _metadata(),
        "created_at": NOW,
        "updated_at": NOW,
        "status": AssetStatus.ACTIVE,
        "lifecycle": AssetLifecycle.VALIDATED,
        "attributes": {"owner": "CKO", "revision": 1},
    }


@pytest.mark.parametrize(
    ("asset_type", "specific"),
    [
        (Asset, {}),
        (DocumentAsset, {"page_count": 12}),
        (ImageAsset, {"width": 1920, "height": 1080}),
        (AudioAsset, {"duration_seconds": 31.5}),
        (
            VideoAsset,
            {"duration_seconds": 90.0, "width": 1920, "height": 1080},
        ),
        (ProjectAsset, {"project_code": "SPR-008B"}),
        (DatabaseAsset, {"database_system": "logical", "schema_name": "cko"}),
        (KnowledgeAsset, {"knowledge_type": "technical-note"}),
        (FolderAsset, {}),
        (
            ReferenceAsset,
            {"target_uri": "urn:cko:asset:external", "reference_type": "cites"},
        ),
    ],
)
def test_constructs_and_round_trips_every_asset_type(
    asset_type: type[Asset], specific: dict[str, object]
) -> None:
    asset = asset_type(**_common(), **specific)

    restored = asset_from_dict(asset.to_dict())
    restored_from_json = asset_type.from_json(asset.to_json())

    assert type(restored) is asset_type
    assert restored.to_dict() == asset.to_dict()
    assert restored_from_json.to_dict() == asset.to_dict()
    assert asset.to_dict()["schema_version"] == "1.0"
    assert asset.to_dict()["kind"] == asset_type.kind


def test_identity_and_equality_are_based_on_canonical_id() -> None:
    asset_id = CanonicalId.new()
    original = DocumentAsset(**_common(asset_id), page_count=1)
    renamed = replace(original, name="Novo nome", page_count=2)
    distinct = replace(original, id=CanonicalId.new())

    assert original == renamed
    assert hash(original) == hash(renamed)
    assert original != distinct
    assert isinstance(original.id, CanonicalId)


def test_asset_aggregates_hash_fingerprint_classification_and_metadata() -> None:
    asset_id = CanonicalId.new()
    digest = AssetHash(
        id=CanonicalId.new(),
        asset_id=asset_id,
        algorithm="SHA-256",
        value="A" * 64,
        calculated_at=NOW,
    )
    fingerprint = AssetFingerprint(
        id=CanonicalId.new(),
        asset_id=asset_id,
        scheme="cko-content-v1",
        value="document:normalized:42",
        generated_at=NOW,
        attributes={"profile": "canonical"},
    )
    classification = AssetClassification(
        id=CanonicalId.new(),
        asset_id=asset_id,
        scheme="cko.asset.class",
        value="technical-document",
        assigned_at=NOW,
        confidence=0.95,
        attributes={"source": "human"},
    )
    asset = DocumentAsset(
        **_common(asset_id),
        hashes=(digest,),
        fingerprints=(fingerprint,),
        classifications=(classification,),
    )

    restored = DocumentAsset.from_json(asset.to_json())

    assert restored.hashes[0].algorithm == "sha256"
    assert restored.fingerprints[0].scheme == "cko-content-v1"
    assert restored.classifications[0].confidence == 0.95
    assert restored.metadata.attributes["source"]["system"] == "unit-test"
    assert AssetHash.from_json(digest.to_json()).to_dict() == digest.to_dict()
    assert (
        AssetFingerprint.from_json(fingerprint.to_json()).to_dict()
        == fingerprint.to_dict()
    )
    assert (
        AssetClassification.from_json(classification.to_json()).to_dict()
        == classification.to_dict()
    )


def test_relation_connects_distinct_canonical_assets_and_round_trips() -> None:
    source = DocumentAsset(**_common())
    target = KnowledgeAsset(**_common())
    relation = AssetRelation(
        id=CanonicalId.new(),
        source_asset_id=source.id,
        target_asset_id=target.id,
        relation_type="derives-from",
        created_at=NOW,
        attributes={"evidence": "manual-review"},
    )

    restored = AssetRelation.from_json(relation.to_json())

    assert restored.to_dict() == relation.to_dict()
    assert restored.source_asset_id == source.id
    assert restored.target_asset_id == target.id
    with pytest.raises(ValueError, match="ativos distintos"):
        replace(relation, target_asset_id=source.id)


def test_models_are_immutable_including_extension_metadata() -> None:
    asset = Asset(**_common())

    with pytest.raises(FrozenInstanceError):
        asset.name = "alterado"  # type: ignore[misc]
    with pytest.raises(TypeError):
        asset.attributes["owner"] = "outro"  # type: ignore[index]
    with pytest.raises(TypeError):
        asset.metadata.attributes["source"]["system"] = "outro"  # type: ignore[index]


def test_rejects_invalid_hashes_relations_and_cross_asset_metadata() -> None:
    asset_id = CanonicalId.new()
    with pytest.raises(ValueError, match="digest sha256"):
        AssetHash(CanonicalId.new(), asset_id, "sha256", "xyz", NOW)
    foreign_hash = AssetHash(
        CanonicalId.new(), CanonicalId.new(), "sha256", "a" * 64, NOW
    )
    with pytest.raises(ValueError, match="hashes"):
        Asset(**_common(asset_id), hashes=(foreign_hash,))
    with pytest.raises(ValueError, match="confidence"):
        AssetClassification(
            CanonicalId.new(), asset_id, "scheme", "value", NOW, 1.1
        )


def test_rejects_invalid_dimensions_dates_and_reference() -> None:
    with pytest.raises(ValueError, match="width"):
        ImageAsset(**_common(), width=0, height=10)
    invalid_dates = _common()
    invalid_dates["updated_at"] = datetime(2026, 7, 13, tzinfo=UTC)
    with pytest.raises(ValueError, match="updated_at"):
        Asset(**invalid_dates)
    with pytest.raises(ValueError, match="target"):
        ReferenceAsset(**_common())
    with pytest.raises(ValueError, match="esquema"):
        ReferenceAsset(**_common(), target_uri="relative/reference")


def test_deserialization_rejects_unknown_schema_kind_and_fields() -> None:
    payload = Asset(**_common()).to_dict()
    with pytest.raises(ValueError, match="schema_version"):
        asset_from_dict({**payload, "schema_version": "2.0"})
    with pytest.raises(ValueError, match="kind"):
        asset_from_dict({**payload, "kind": "parallel-entity"})
    with pytest.raises(ValueError, match="campos desconhecidos"):
        asset_from_dict({**payload, "engine_private_state": True})
