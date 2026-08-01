"""Unit tests for the SPR-008C Canonical Inventory Engine."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime
from types import MappingProxyType

import pytest

from cko.core import (
    Asset,
    AssetClassification,
    AssetFingerprint,
    AssetHash,
    AssetLifecycle,
    AssetStatus,
    CanonicalId,
    DocumentAsset,
    KnowledgeAsset,
    UniversalMetadata,
)
from cko.core.inventory import (
    AssetNotFoundError,
    DuplicateAssetError,
    Inventory,
    InventoryBuilder,
    InventoryCollection,
    InventoryFilter,
    InventoryItem,
    InventoryQuery,
    InventoryResult,
    InventoryService,
    InventorySnapshot,
    InventoryStatistics,
    InventoryValidationError,
    InventoryValidator,
)


NOW = datetime(2026, 7, 14, 20, 0, tzinfo=UTC)


def _metadata() -> UniversalMetadata:
    return UniversalMetadata(
        media_type="application/octet-stream",
        created_at=NOW,
        modified_at=NOW,
        language="pt-BR",
        attributes={"source": "unit-test"},
    )


def _asset(
    name: str = "Canonical asset",
    *,
    status: AssetStatus = AssetStatus.ACTIVE,
    lifecycle: AssetLifecycle = AssetLifecycle.VALIDATED,
    classification: tuple[str, str] | None = None,
) -> Asset:
    asset_id = CanonicalId.new()
    classifications = ()
    if classification is not None:
        classifications = (
            AssetClassification(
                id=CanonicalId.new(),
                asset_id=asset_id,
                scheme=classification[0],
                value=classification[1],
                assigned_at=NOW,
            ),
        )
    return Asset(
        id=asset_id,
        name=name,
        metadata=_metadata(),
        created_at=NOW,
        updated_at=NOW,
        status=status,
        lifecycle=lifecycle,
        classifications=classifications,
    )


def _document(name: str = "Document") -> DocumentAsset:
    asset = _asset(name)
    return DocumentAsset(
        id=asset.id,
        name=asset.name,
        metadata=asset.metadata,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        status=asset.status,
        lifecycle=asset.lifecycle,
        page_count=3,
    )


def test_inventory_register_find_replace_remove_and_domain_errors() -> None:
    inventory = Inventory(CanonicalId.new(), "Primary")
    original = _asset()

    item = inventory.register(original)

    assert item.id == original.id
    assert inventory.find(original.id) is original
    assert inventory.require(original.id) is original
    assert inventory.revision == 1
    with pytest.raises(DuplicateAssetError):
        inventory.register(original)

    replacement = replace(original, name="Revised")
    inventory.register(replacement, replace=True)
    assert inventory.require(original.id).name == "Revised"
    assert inventory.remove(original.id) == replacement
    assert len(inventory) == 0
    assert inventory.find(original.id) is None
    with pytest.raises(AssetNotFoundError):
        inventory.require(original.id)
    with pytest.raises(AssetNotFoundError):
        inventory.remove(original.id)


def test_queries_filters_sorting_and_pagination() -> None:
    classified = _asset("Zulu", classification=("cko.class", "technical"))
    inactive = _asset(
        "Alpha",
        status=AssetStatus.INACTIVE,
        lifecycle=AssetLifecycle.DRAFT,
    )
    document = _document("Middle")
    inventory = Inventory(
        CanonicalId.new(),
        "Queryable",
        (classified, inactive, document),
    )

    assert inventory.find_by_type(DocumentAsset).items[0].asset == document
    assert inventory.find_by_type("document").items[0].asset == document
    assert inventory.find_by_status(AssetStatus.INACTIVE).items[0].asset == inactive
    assert inventory.find_by_lifecycle(AssetLifecycle.DRAFT).items[0].asset == inactive
    assert inventory.find_by_classification(
        "cko.class", "technical"
    ).items[0].asset == classified

    result = inventory.query(
        InventoryQuery(
            filter=InventoryFilter(
                ids=(classified.id, inactive.id),
                types=("asset",),
            ),
            offset=1,
            limit=1,
            sort_by="name",
        )
    )
    assert result.total == 2
    assert result.collection.items[0].asset.name == "Zulu"
    assert result.to_dict()["offset"] == 1


def test_snapshot_is_immutable_detached_and_serializable() -> None:
    asset = _asset("Snapshot asset")
    inventory = Inventory(CanonicalId.new(), "Snapshot source", (asset,))

    snapshot = inventory.snapshot()
    encoded = snapshot.to_json()
    restored = InventorySnapshot.from_json(encoded)
    inventory.remove(asset.id)

    assert len(snapshot.collection) == 1
    assert restored.to_dict() == snapshot.to_dict()
    assert snapshot.collection.get(asset.id) is not None
    with pytest.raises(FrozenInstanceError):
        snapshot.revision = 99  # type: ignore[misc]
    with pytest.raises(ValueError, match="object"):
        InventorySnapshot.from_json("[]")


def test_statistics_summary_and_read_only_breakdowns() -> None:
    first = _asset("One", classification=("scheme", "value"))
    second = _asset("Two", status=AssetStatus.ARCHIVED)
    inventory = Inventory(CanonicalId.new(), "Statistics", (first, second))

    statistics = inventory.statistics()
    summary = inventory.summary()

    assert statistics.total == 2
    assert statistics.by_type == {"asset": 2}
    assert statistics.by_status == {"active": 1, "archived": 1}
    assert statistics.by_classification == {"scheme:value": 1}
    assert summary.statistics is not statistics
    assert summary.to_dict()["statistics"]["total"] == 2  # type: ignore[index]
    with pytest.raises(TypeError):
        statistics.by_type["asset"] = 3  # type: ignore[index]


def test_inventory_round_trip_preserves_revision_and_asset_subtypes() -> None:
    document = _document()
    inventory = Inventory(CanonicalId.new(), "Serialized", (document,))
    inventory.register(_asset())
    inventory.remove(document.id)

    restored = Inventory.from_json(inventory.to_json())

    assert restored.to_dict() == inventory.to_dict()
    assert restored.revision == 3
    with pytest.raises(ValueError, match="object"):
        Inventory.from_json("[]")
    invalid = inventory.to_dict()
    invalid["revision"] = 0
    with pytest.raises(ValueError, match="revision"):
        Inventory.from_dict(invalid)


def test_builder_and_service_cover_canonical_use_cases() -> None:
    first = _asset("First")
    second = _asset("Second")
    inventory_id = CanonicalId.new()
    builder = InventoryBuilder().identified_by(inventory_id).named("Built")
    inventory = builder.add(first).extend((second,)).build()
    service = InventoryService(inventory)

    assert service.inventory.id == inventory_id
    assert service.snapshot().revision == 2
    assert service.statistics().total == 2
    assert service.summary().name == "Built"
    assert service.validate() == ()
    assert service.query(InventoryQuery()).total == 2
    assert service.remove(first.id) == first
    assert service.register(first).asset == first
    with pytest.raises(DuplicateAssetError):
        InventoryBuilder().add(first).add(first)
    with pytest.raises(TypeError, match="Asset"):
        InventoryBuilder().add("invalid")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="id"):
        InventoryBuilder().named("Missing id").build()
    with pytest.raises(ValueError, match="name"):
        InventoryBuilder().identified_by(inventory_id).build()


def test_validator_reports_key_mismatch_and_duplicate_nested_ids() -> None:
    first = _asset("First", classification=("scheme", "first"))
    second = _asset("Second", classification=("scheme", "second"))
    duplicate = replace(second.classifications[0], id=first.classifications[0].id)
    second = replace(second, classifications=(duplicate,))
    items = {
        CanonicalId.new(): InventoryItem(first),
        second.id: InventoryItem(second),
    }
    validator = InventoryValidator()

    violations = validator.validate(items)

    assert any("key differs" in violation for violation in violations)
    assert any("duplicate nested" in violation for violation in violations)
    with pytest.raises(InventoryValidationError) as captured:
        validator.ensure_valid(items)
    assert captured.value.violations == violations


def test_collection_and_value_object_validation() -> None:
    item = InventoryItem(_asset())
    collection = InventoryCollection((item,))

    assert InventoryCollection.from_list(collection.to_list()) == collection
    assert list(collection) == [item]
    with pytest.raises(ValueError, match="duplicate"):
        InventoryCollection((item, item))
    with pytest.raises(ValueError, match="list"):
        InventoryCollection.from_list({})
    with pytest.raises(TypeError, match="Asset"):
        InventoryItem("invalid")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="types"):
        InventoryFilter(types=("",))
    with pytest.raises(ValueError, match="classifications"):
        InventoryFilter(classifications=(("", "value"),))


@pytest.mark.parametrize(
    "query",
    [
        InventoryQuery(offset=0),
        InventoryQuery(limit=1),
        InventoryQuery(sort_by="type", descending=True),
    ],
)
def test_valid_query_variants(query: InventoryQuery) -> None:
    assert isinstance(query.filter, InventoryFilter)


def test_rejects_invalid_queries_statistics_and_construction() -> None:
    with pytest.raises(ValueError, match="offset"):
        InventoryQuery(offset=-1)
    with pytest.raises(ValueError, match="limit"):
        InventoryQuery(limit=0)
    with pytest.raises(ValueError, match="sort_by"):
        InventoryQuery(sort_by="unknown")
    with pytest.raises(ValueError, match="total"):
        InventoryStatistics(-1)
    with pytest.raises(ValueError, match="negative counts"):
        InventoryStatistics(0, by_type={"asset": -1})
    with pytest.raises(ValueError, match="name"):
        Inventory(CanonicalId.new(), " ")
    with pytest.raises(TypeError, match="Inventory"):
        InventoryService("invalid")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="violations"):
        InventoryValidationError(())


def test_statistics_accepts_general_mappings_but_freezes_them() -> None:
    statistics = InventoryStatistics(
        1,
        by_type=MappingProxyType({"asset": 1}),
    )
    assert dict(statistics.by_type) == {"asset": 1}


def test_filter_rejects_each_non_matching_canonical_dimension() -> None:
    classified = _asset("Filtered", classification=("scheme", "value"))

    assert not InventoryFilter(ids=(CanonicalId.new(),)).matches(classified)
    assert not InventoryFilter(types=("document",)).matches(classified)
    assert not InventoryFilter(statuses=(AssetStatus.ARCHIVED,)).matches(classified)
    assert not InventoryFilter(
        lifecycles=(AssetLifecycle.DRAFT,)
    ).matches(classified)
    assert not InventoryFilter(
        classifications=(("scheme", "other"),)
    ).matches(classified)
    coerced = InventoryFilter(statuses=("active",), lifecycles=("validated",))
    assert coerced.matches(classified)


def test_snapshot_collection_result_and_statistics_reject_invalid_state() -> None:
    inventory_id = CanonicalId.new()
    collection = InventoryCollection()

    with pytest.raises(TypeError, match="InventoryItem"):
        InventoryCollection(("invalid",))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="every item"):
        InventoryCollection.from_list(["invalid"])
    with pytest.raises(ValueError, match="asset"):
        InventoryItem.from_dict({})
    with pytest.raises(TypeError, match="CanonicalId"):
        InventorySnapshot("invalid", "name", 0, collection)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="name"):
        InventorySnapshot(inventory_id, " ", 0, collection)
    with pytest.raises(ValueError, match="revision"):
        InventorySnapshot(inventory_id, "name", -1, collection)
    with pytest.raises(ValueError, match="schema_version"):
        InventorySnapshot.from_dict({"schema_version": "2.0"})
    with pytest.raises(ValueError, match="total"):
        InventoryResult(collection, -1, 0, None)
    with pytest.raises(ValueError, match="limit"):
        InventoryResult(collection, 0, 0, 0)


def test_inventory_rejects_invalid_inputs_and_serialized_envelopes() -> None:
    inventory_id = CanonicalId.new()
    with pytest.raises(TypeError, match="CanonicalId"):
        Inventory("invalid", "name")  # type: ignore[arg-type]
    inventory = Inventory(inventory_id, "name")
    with pytest.raises(TypeError, match="Asset"):
        inventory.register("invalid")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="schema_version"):
        Inventory.from_dict({"schema_version": "2.0"})
    with pytest.raises(ValueError, match="assets"):
        Inventory.from_dict(
            {
                "schema_version": "1.0",
                "inventory_id": str(inventory_id),
                "name": "name",
                "revision": 0,
                "assets": {},
            }
        )
    with pytest.raises(ValueError, match="every asset"):
        Inventory.from_dict(
            {
                "schema_version": "1.0",
                "inventory_id": str(inventory_id),
                "name": "name",
                "revision": 0,
                "assets": ["invalid"],
            }
        )


def test_query_executes_all_sort_modes_and_open_ended_pagination() -> None:
    first = _asset("Zulu")
    second = _document("Alpha")
    inventory = Inventory(CanonicalId.new(), "Sorts", (first, second))

    by_identifier = inventory.query(InventoryQuery(sort_by="id"))
    by_type = inventory.query(
        InventoryQuery(sort_by="type", descending=True, offset=1)
    )

    assert by_identifier.total == 2
    assert len(by_type.collection) == 1
    assert by_type.limit is None


def test_validator_covers_fingerprint_and_hash_consistency() -> None:
    first_id = CanonicalId.new()
    second_id = CanonicalId.new()
    nested_id = CanonicalId.new()
    first_fingerprint = AssetFingerprint(
        nested_id,
        first_id,
        "canonical",
        "first",
        NOW,
    )
    second_fingerprint = AssetFingerprint(
        nested_id,
        second_id,
        "canonical",
        "second",
        NOW,
    )
    first_hash = AssetHash(
        CanonicalId.new(),
        first_id,
        "sha256",
        "a" * 64,
        NOW,
    )
    second_hash = AssetHash(
        first_hash.id,
        second_id,
        "sha256",
        "b" * 64,
        NOW,
    )
    first = replace(
        _asset("First"),
        id=first_id,
        fingerprints=(first_fingerprint,),
        hashes=(first_hash,),
    )
    second = replace(
        _asset("Second"),
        id=second_id,
        fingerprints=(second_fingerprint,),
        hashes=(second_hash,),
    )
    inventory = Inventory(CanonicalId.new(), "Atomic", (first,))
    with pytest.raises(InventoryValidationError):
        inventory.register(second)
    assert len(inventory) == 1
    assert inventory.revision == 1

    object.__setattr__(first_fingerprint, "asset_id", CanonicalId.new())
    object.__setattr__(first_hash, "asset_id", CanonicalId.new())

    violations = InventoryValidator().validate(
        {first.id: InventoryItem(first), second.id: InventoryItem(second)}
    )

    assert any("fingerprint" in violation for violation in violations)
    assert any("hash" in violation for violation in violations)
    assert sum("duplicate nested" in violation for violation in violations) == 2
