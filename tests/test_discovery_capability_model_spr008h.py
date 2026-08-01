"""Capability model foundation and regression contracts for SPR-008H."""

from __future__ import annotations

import ast
import inspect
import json
import logging
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path
from typing import Sequence

import pytest

from cko.core import SemanticVersion
from cko.core.discovery import (
    CAPABILITY_SCHEMA_VERSION,
    Capability,
    CapabilityCategory,
    CapabilityConflictError,
    CapabilityDependencyError,
    CapabilityNegotiationEngine,
    CapabilityReport,
    CapabilityRequirement,
    CapabilityRequirementType,
    CapabilityResolver,
    CapabilitySet,
    CapabilityValidationEngine,
    InvalidCapabilityError,
)


NOW = datetime(2026, 7, 15, 20, 0, tzinfo=UTC)
V1 = SemanticVersion.parse("1.0.0")
V2 = SemanticVersion.parse("2.0.0")


def requirement(
    capability_id: str,
    requirement_type: CapabilityRequirementType = (
        CapabilityRequirementType.REQUIRED
    ),
    *,
    minimum: SemanticVersion | None = None,
    incompatible: Sequence[SemanticVersion] = (),
) -> CapabilityRequirement:
    """Build a concise requirement used by capability tests."""
    return CapabilityRequirement(
        capability_id,
        requirement_type,
        minimum,
        incompatible,
        "SPR-008H test requirement",
    )


def capability(
    capability_id: str,
    *,
    version: SemanticVersion = V1,
    dependencies: Sequence[CapabilityRequirement] = (),
    incompatibilities: Sequence[CapabilityRequirement] = (),
) -> Capability:
    """Build a complete immutable capability declaration."""
    return Capability(
        id=capability_id,
        name=f"Capability {capability_id}",
        description=f"Canonical behavior for {capability_id}",
        category=CapabilityCategory.DISCOVERY,
        version=version,
        dependencies=dependencies,
        incompatibilities=incompatibilities,
        metadata={"owner": "cko", "flags": ["deterministic"]},
    )


def test_capability_is_deeply_immutable_and_versioned() -> None:
    model = capability("discovery.list")

    with pytest.raises(FrozenInstanceError):
        model.name = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        model.metadata["owner"] = "other"  # type: ignore[index]
    assert model.metadata["flags"] == ("deterministic",)
    assert model.schema_version == CAPABILITY_SCHEMA_VERSION


def test_capability_round_trip_and_json_are_deterministic() -> None:
    dependency = requirement("discovery.read", minimum=V1)
    conflict = requirement(
        "discovery.legacy",
        CapabilityRequirementType.PROHIBITED,
        incompatible=(V1,),
    )
    model = capability(
        "discovery.list",
        dependencies=(dependency,),
        incompatibilities=(conflict,),
    )

    restored = Capability.from_json(model.to_json())

    assert restored == model
    assert restored.to_json() == model.to_json()
    assert list(json.loads(model.to_json())) == sorted(model.to_dict())


def test_requirement_round_trip_supports_all_semantics() -> None:
    for kind in CapabilityRequirementType:
        model = requirement(
            "discovery.read",
            kind,
            minimum=V1,
            incompatible=(V2,),
        )
        assert CapabilityRequirement.from_json(model.to_json()) == model


def test_strict_deserialization_rejects_unknown_fields_and_schema() -> None:
    payload = capability("discovery.list").to_dict()
    payload["unknown"] = True
    with pytest.raises(InvalidCapabilityError, match="unknown"):
        Capability.from_dict(payload)

    set_payload = CapabilitySet().to_dict()
    set_payload["schema_version"] = "2.0"
    with pytest.raises(InvalidCapabilityError, match="schema_version"):
        CapabilitySet.from_dict(set_payload)
    with pytest.raises(InvalidCapabilityError, match="JSON"):
        Capability.from_json("[]")


def test_invalid_capability_invariants_are_rejected() -> None:
    with pytest.raises(InvalidCapabilityError):
        capability("")
    with pytest.raises(InvalidCapabilityError, match="prohibited"):
        capability(
            "discovery.list",
            dependencies=(
                requirement(
                    "discovery.read",
                    CapabilityRequirementType.PROHIBITED,
                ),
            ),
        )
    with pytest.raises(InvalidCapabilityError, match="itself"):
        capability(
            "discovery.list",
            dependencies=(requirement("discovery.list"),),
        )


def test_metadata_and_requirement_validation_reject_invalid_values() -> None:
    assert capability("discovery.float").metadata["owner"] == "cko"
    with pytest.raises(InvalidCapabilityError, match="finite"):
        Capability(
            "discovery.invalid",
            "Invalid",
            "Invalid metadata",
            CapabilityCategory.DISCOVERY,
            V1,
            metadata={"score": float("inf")},
        )
    with pytest.raises(InvalidCapabilityError, match="keys"):
        Capability(
            "discovery.invalid",
            "Invalid",
            "Invalid metadata",
            CapabilityCategory.DISCOVERY,
            V1,
            metadata={"": True},
        )
    with pytest.raises(InvalidCapabilityError, match="unsupported metadata"):
        Capability(
            "discovery.invalid",
            "Invalid",
            "Invalid metadata",
            CapabilityCategory.DISCOVERY,
            V1,
            metadata={"value": object()},
        )
    with pytest.raises(InvalidCapabilityError, match="minimum_version"):
        CapabilityRequirement(
            "discovery.read",
            CapabilityRequirementType.REQUIRED,
            "1.0.0",  # type: ignore[arg-type]
        )
    with pytest.raises(InvalidCapabilityError, match="incompatible_versions"):
        CapabilityRequirement(
            "discovery.read",
            CapabilityRequirementType.REQUIRED,
            incompatible_versions=("2.0.0",),  # type: ignore[arg-type]
        )


def test_requirement_satisfaction_handles_prohibition_and_wrong_identity() -> None:
    prohibition = requirement(
        "discovery.legacy",
        CapabilityRequirementType.PROHIBITED,
        incompatible=(V1,),
    )
    legacy_v1 = capability("discovery.legacy", version=V1)
    legacy_v2 = capability("discovery.legacy", version=V2)
    required = requirement("discovery.read")

    assert prohibition.is_satisfied_by(None)
    assert not prohibition.is_satisfied_by(legacy_v1)
    assert prohibition.is_satisfied_by(legacy_v2)
    assert not required.is_satisfied_by(legacy_v1)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("incompatible_versions", "invalid", "array"),
        ("reason", 7, "reason"),
        ("requirement_type", "unknown", "requirement_type"),
        ("minimum_version", 1, "minimum_version"),
        ("minimum_version", "invalid", "minimum_version"),
    ],
)
def test_requirement_deserialization_rejects_invalid_fields(
    field: str, value: object, message: str
) -> None:
    payload = requirement("discovery.read").to_dict()
    payload[field] = value

    with pytest.raises(InvalidCapabilityError, match=message):
        CapabilityRequirement.from_dict(payload)


def test_capability_deserialization_rejects_invalid_nested_fields() -> None:
    base = capability("discovery.read").to_dict()
    mutations = (
        ("dependencies", {}, "dependencies"),
        ("incompatibilities", {}, "incompatibilities"),
        ("metadata", [], "metadata"),
        ("dependencies", ["invalid"], "dependencies"),
        ("incompatibilities", ["invalid"], "incompatibilities"),
        ("category", "unknown", "category"),
        ("version", 1, "version"),
        ("version", "invalid", "version"),
    )
    for field, value, message in mutations:
        payload = dict(base)
        payload[field] = value
        with pytest.raises(InvalidCapabilityError, match=message):
            Capability.from_dict(payload)


def test_set_and_report_reject_invalid_public_envelopes() -> None:
    with pytest.raises(TypeError, match="CapabilitySet"):
        CapabilitySet().union(object())  # type: ignore[arg-type]
    payload = CapabilitySet().to_dict()
    payload["capabilities"] = ["invalid"]
    with pytest.raises(InvalidCapabilityError, match="capabilities"):
        CapabilitySet.from_dict(payload)

    valid = CapabilityValidationEngine().validate(CapabilitySet(), timestamp=NOW)
    report_payload = valid.to_dict()
    report_payload["timestamp"] = "invalid"
    with pytest.raises(InvalidCapabilityError, match="timestamp"):
        CapabilityReport.from_dict(report_payload)
    report_payload = valid.to_dict()
    report_payload["justifications"] = {"key": "invalid"}
    with pytest.raises(InvalidCapabilityError, match="justifications"):
        CapabilityReport.from_dict(report_payload)


def test_capability_set_is_ordered_and_round_trips() -> None:
    models = CapabilitySet.of(
        [capability("discovery.z"), capability("discovery.a")]
    )

    assert [item.id for item in models] == ["discovery.a", "discovery.z"]
    assert "discovery.a" in models
    assert CapabilitySet.from_json(models.to_json()) == models
    assert models.to_json() == CapabilitySet.of(reversed(models.capabilities)).to_json()


def test_capability_set_union_difference_and_intersection() -> None:
    first = capability("discovery.first")
    second = capability("discovery.second")
    left = CapabilitySet.of((first,))
    right = CapabilitySet.of((second,))

    union = left | right

    assert union == CapabilitySet.of((first, second))
    assert union - right == left
    assert union & left == left
    assert left < union
    assert union > left


def test_capability_set_comparison_is_version_aware() -> None:
    lower = CapabilitySet.of((capability("discovery.read", version=V1),))
    higher = CapabilitySet.of((capability("discovery.read", version=V2),))

    assert lower <= higher
    assert not higher <= lower
    with pytest.raises(InvalidCapabilityError, match="conflicting"):
        lower | higher


def test_capability_set_rejects_duplicate_identities() -> None:
    with pytest.raises(InvalidCapabilityError, match="unique"):
        CapabilitySet.of(
            (
                capability("discovery.read", version=V1),
                capability("discovery.read", version=V2),
            )
        )


def test_validation_accepts_satisfied_required_and_optional_requirements() -> None:
    models = CapabilitySet.of((capability("discovery.read", version=V2),))
    requirements = (
        requirement("discovery.read", minimum=V1),
        requirement(
            "discovery.optional",
            CapabilityRequirementType.OPTIONAL,
        ),
    )

    report = CapabilityValidationEngine().validate(
        models, requirements, timestamp=NOW
    )

    assert report.is_valid
    assert report.accepted == models
    assert not report.rejected
    assert not report.missing


def test_validation_reports_missing_and_minimum_version() -> None:
    models = CapabilitySet.of((capability("discovery.read", version=V1),))
    requirements = (
        requirement("discovery.write"),
        requirement("discovery.read", minimum=V2),
    )

    report = CapabilityValidationEngine().validate(
        models, requirements, timestamp=NOW
    )

    assert not report.is_valid
    assert {item.capability_id for item in report.missing} == {
        "discovery.read",
        "discovery.write",
    }
    assert "below minimum" in report.justifications["discovery.read"][0]


def test_validation_rejects_explicitly_incompatible_version() -> None:
    models = CapabilitySet.of((capability("discovery.read", version=V2),))
    constraint = requirement("discovery.read", incompatible=(V2,))

    report = CapabilityValidationEngine().validate(
        models, (constraint,), timestamp=NOW
    )

    assert not report.is_valid
    assert report.missing == (constraint,)
    assert "explicitly incompatible" in report.justifications["discovery.read"][0]


def test_validation_detects_prohibited_requirement() -> None:
    legacy = capability("discovery.legacy")
    prohibited = requirement(
        legacy.id, CapabilityRequirementType.PROHIBITED
    )

    report = CapabilityValidationEngine().validate(
        CapabilitySet.of((legacy,)), (prohibited,), timestamp=NOW
    )

    assert not report.is_valid
    assert report.rejected == CapabilitySet.of((legacy,))
    assert report.conflicting == CapabilitySet.of((legacy,))


def test_validation_detects_capability_conflicts() -> None:
    modern = capability(
        "discovery.modern",
        incompatibilities=(
            requirement(
                "discovery.legacy",
                CapabilityRequirementType.PROHIBITED,
            ),
        ),
    )
    legacy = capability("discovery.legacy")
    models = CapabilitySet.of((modern, legacy))

    report = CapabilityValidationEngine().validate(models, timestamp=NOW)

    assert not report.is_valid
    assert {item.id for item in report.conflicting} == {
        "discovery.legacy",
        "discovery.modern",
    }
    with pytest.raises(CapabilityConflictError):
        CapabilityValidationEngine().ensure_valid(models)


def test_validation_detects_missing_dependency() -> None:
    listing = capability(
        "discovery.list",
        dependencies=(requirement("discovery.read", minimum=V1),),
    )

    report = CapabilityValidationEngine().validate(
        CapabilitySet.of((listing,)), timestamp=NOW
    )

    assert not report.is_valid
    assert report.rejected == CapabilitySet.of((listing,))
    assert report.missing[0].capability_id == "discovery.read"
    with pytest.raises(CapabilityDependencyError):
        CapabilityValidationEngine().ensure_valid(CapabilitySet.of((listing,)))


def test_resolver_expands_transitive_dependencies() -> None:
    read = capability("discovery.read")
    parse = capability(
        "discovery.parse",
        dependencies=(requirement(read.id),),
    )
    listing = capability(
        "discovery.list",
        dependencies=(requirement(parse.id),),
    )
    available = CapabilitySet.of((listing, read, parse))

    resolved = CapabilityResolver().resolve(
        CapabilitySet.of((listing,)), available
    )

    assert resolved == available


def test_resolver_skips_unavailable_optional_dependency() -> None:
    listing = capability(
        "discovery.list",
        dependencies=(
            requirement(
                "discovery.preview",
                CapabilityRequirementType.OPTIONAL,
            ),
        ),
    )

    resolved = CapabilityResolver().resolve(
        CapabilitySet.of((listing,)), CapabilitySet.of((listing,))
    )

    assert resolved == CapabilitySet.of((listing,))


def test_resolver_rejects_unavailable_or_invalid_dependency() -> None:
    listing = capability(
        "discovery.list",
        dependencies=(requirement("discovery.read", minimum=V2),),
    )
    with pytest.raises(CapabilityDependencyError, match="unavailable"):
        CapabilityResolver().resolve(
            CapabilitySet.of((listing,)), CapabilitySet.of((listing,))
        )
    with pytest.raises(CapabilityDependencyError, match="version"):
        CapabilityResolver().resolve(
            CapabilitySet.of((listing,)),
            CapabilitySet.of((listing, capability("discovery.read"))),
        )


def test_negotiation_selects_lowest_common_version_deterministically() -> None:
    sets = (
        CapabilitySet.of((capability("discovery.read", version=V2),)),
        CapabilitySet.of((capability("discovery.read", version=V1),)),
        CapabilitySet.of((capability("discovery.read", version=V2),)),
        CapabilitySet.of((capability("discovery.read", version=V1),)),
    )

    first = CapabilityNegotiationEngine().negotiate(*sets, timestamp=NOW)
    second = CapabilityNegotiationEngine().negotiate(*sets, timestamp=NOW)

    assert first.is_valid
    assert first.accepted.get("discovery.read").version == V1  # type: ignore[union-attr]
    assert first.to_json() == second.to_json()


def test_negotiation_rejects_capability_not_supported_by_every_role() -> None:
    shared = capability("discovery.shared")
    provider_only = capability("discovery.provider-only")
    provider = CapabilitySet.of((shared, provider_only))
    common = CapabilitySet.of((shared,))

    report = CapabilityNegotiationEngine().negotiate(
        provider, common, common, common, timestamp=NOW
    )

    assert report.is_valid
    assert report.accepted == common
    assert report.rejected == CapabilitySet.of((provider_only,))
    assert "pipeline" in report.justifications[provider_only.id][0]


def test_negotiation_validates_required_capabilities() -> None:
    empty = CapabilitySet()
    required = requirement("discovery.required")

    report = CapabilityNegotiationEngine().negotiate(
        empty,
        empty,
        empty,
        empty,
        (required,),
        timestamp=NOW,
    )

    assert not report.is_valid
    assert report.missing == (required,)


def test_negotiation_emits_structured_log_events(caplog: pytest.LogCaptureFixture) -> None:
    shared = CapabilitySet.of((capability("discovery.shared"),))
    caplog.set_level(logging.INFO, logger="cko.core.discovery.capability")

    CapabilityNegotiationEngine().negotiate(
        shared, shared, shared, shared, timestamp=NOW
    )

    events = [getattr(record, "event", None) for record in caplog.records]
    assert events == [
        "discovery.capability.negotiation.started",
        "discovery.capability.negotiation.completed",
    ]
    assert caplog.records[-1].context["accepted_count"] == 1


def test_capability_report_round_trip_is_auditable() -> None:
    models = CapabilitySet.of((capability("discovery.read"),))
    report = CapabilityValidationEngine().validate(models, timestamp=NOW)

    restored = CapabilityReport.from_json(report.to_json())

    assert restored == report
    assert restored.timestamp == NOW
    with pytest.raises(TypeError):
        restored.justifications["other"] = ("invalid",)  # type: ignore[index]


def test_public_api_exports_canonical_capability_contracts() -> None:
    from cko.core import discovery

    names = {
        "Capability",
        "CapabilityCategory",
        "CapabilityNegotiationEngine",
        "CapabilityReport",
        "CapabilityRequirement",
        "CapabilityResolver",
        "CapabilitySet",
        "CapabilityValidationEngine",
    }

    assert names.issubset(discovery.__all__)
    for name in names:
        assert getattr(discovery, name).__module__.startswith(
            "cko.core.discovery"
        )


def test_public_type_hints_docstrings_utf8_and_pep8_surface() -> None:
    public = (
        Capability,
        CapabilitySet,
        CapabilityRequirement,
        CapabilityReport,
        CapabilityValidationEngine,
        CapabilityNegotiationEngine,
        CapabilityResolver,
    )
    for model in public:
        assert inspect.getdoc(model)
    for method in (
        Capability.from_dict,
        CapabilitySet.union,
        CapabilityValidationEngine.validate,
        CapabilityNegotiationEngine.negotiate,
        CapabilityResolver.resolve,
    ):
        assert inspect.getdoc(method)
        assert inspect.signature(method).return_annotation

    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    for name in (
        "capability_errors.py",
        "capability_models.py",
        "capability_validation.py",
        "capability_negotiation.py",
    ):
        content = (root / name).read_bytes()
        assert not content.startswith(b"\xef\xbb\xbf")
        text = content.decode("utf-8")
        assert max(map(len, text.splitlines())) <= 99
        assert "TODO" not in text
        assert "NotImplementedError" not in text


def test_capability_modules_have_no_infrastructure_imports() -> None:
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    forbidden = {
        "os",
        "pathlib",
        "sqlite3",
        "requests",
        "urllib",
        "threading",
        "multiprocessing",
        "cko.core.inventory",
    }
    for path in root.glob("capability_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        assert not any(
            imported == blocked or imported.startswith(f"{blocked}.")
            for imported in imports
            for blocked in forbidden
        )
