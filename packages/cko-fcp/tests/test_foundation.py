from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import ast
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from cko_fcp import (
    CapabilityAbsentError,
    CapabilityProfile,
    CatalogRecord,
    FCPVersion,
    IdentityError,
    InvalidEnvelopeError,
    InvalidLifecycleTransitionError,
    InvalidRecordError,
    Lifecycle,
    Maturity,
    OperationEnvelope,
    PageRequest,
    Publication,
    RecordState,
    SourceIdentity,
    Trust,
    UnsupportedVersionError,
    Visibility,
    canonical_digest,
    canonical_json,
    negotiate,
    transition,
)
from cko_fcp._validation import strict_mapping


UTC = timezone.utc
FIXTURES = Path(__file__).parent / "fixtures"


def state(
    maturity: Maturity = Maturity.VERIFIED,
    publication: Publication = Publication.PUBLISHED,
    visibility: Visibility = Visibility.INSTITUTIONAL,
    trust: Trust = Trust.T2,
) -> RecordState:
    return RecordState(maturity, publication, visibility, trust)


def record(**changes: object) -> CatalogRecord:
    values: dict[str, object] = {
        "record_id": "record:synthetic:001",
        "record_version": "rv-001",
        "fcp_version": FCPVersion(1, 0),
        "asset_class": "dataset",
        "asset_type": "synthetic-table",
        "purpose": "Contract conformance testing",
        "description": "Synthetic conformance record",
        "source_identity": SourceIdentity("source:synthetic", "local:synthetic:001", "sr-001"),
        "authority_refs": ("authority:synthetic:catalog",),
        "owner_ref": "actor:synthetic:owner",
        "steward_ref": "actor:synthetic:steward",
        "custody_refs": (),
        "state": state(),
        "access_policy_refs": ("policy:synthetic:access",),
        "provenance_refs": ("provenance:synthetic:observation",),
        "relationship_refs": (),
        "limitation_refs": ("limit:synthetic-only",),
        "lifecycle": Lifecycle(
            datetime(2026, 1, 1, 12, tzinfo=UTC),
            datetime(2027, 1, 1, 12, tzinfo=UTC),
            "policy:synthetic:retention",
            "policy:synthetic:withdrawal",
        ),
    }
    values.update(changes)
    return CatalogRecord(**values)  # type: ignore[arg-type]


class LogicalTypesTest(unittest.TestCase):
    def test_version_is_strict_and_orderable(self) -> None:
        self.assertEqual(FCPVersion.parse("1.2"), FCPVersion(1, 2))
        for invalid in ("1", "1.2.3", "01.2", "1.-1", 1.2):
            with self.subTest(invalid=invalid), self.assertRaises(Exception):
                FCPVersion.parse(invalid)

    def test_identity_preserves_opaque_values_and_is_immutable(self) -> None:
        identity = SourceIdentity("SOURCE-A", " Mixed/Case ".strip(), None)
        self.assertEqual(identity.local_id, "Mixed/Case")
        with self.assertRaises(FrozenInstanceError):
            identity.local_id = "rewritten"  # type: ignore[misc]
        with self.assertRaises(IdentityError):
            SourceIdentity(" source", "local")

    def test_closed_schema_rejects_missing_and_unknown_fields(self) -> None:
        valid = {"source_id": "source", "local_id": "local", "source_revision": None}
        self.assertEqual(SourceIdentity.from_dict(valid).source_id, "source")
        with self.assertRaises(IdentityError):
            SourceIdentity.from_dict({**valid, "unknown": True})
        with self.assertRaises(IdentityError):
            SourceIdentity.from_dict({"source_id": "source", "local_id": "local"})

    def test_strict_validation_does_not_coerce(self) -> None:
        with self.assertRaises(Exception):
            SourceIdentity(123, "local")  # type: ignore[arg-type]
        with self.assertRaises(Exception):
            FCPVersion(True, 0)  # type: ignore[arg-type]


class RecordTest(unittest.TestCase):
    def test_valid_record_and_canonical_cardinality_order(self) -> None:
        item = record(authority_refs=("z", "a"))
        self.assertEqual(item.authority_refs, ("a", "z"))

    def test_duplicate_and_missing_cardinalities_fail(self) -> None:
        with self.assertRaises(InvalidRecordError):
            record(authority_refs=())
        with self.assertRaises(InvalidRecordError):
            record(provenance_refs=("p", "p"))

    def test_four_axes_remain_independent(self) -> None:
        item = record(state=state(visibility=Visibility.RESTRICTED))
        self.assertEqual(item.state.maturity, Maturity.VERIFIED)
        self.assertEqual(item.state.publication, Publication.PUBLISHED)
        self.assertEqual(item.state.visibility, Visibility.RESTRICTED)
        self.assertEqual(item.state.trust, Trust.T2)

    def test_record_invariants_fail_closed(self) -> None:
        invalid_states = (
            state(Maturity.LOCATED, Publication.PUBLISHED, trust=Trust.T2),
            state(Maturity.VERIFIED, Publication.UNPUBLISHED, trust=Trust.T1),
            state(Maturity.OFFICIAL, Publication.PUBLISHED, trust=Trust.T3),
        )
        for invalid in invalid_states:
            with self.subTest(invalid=invalid), self.assertRaises(InvalidRecordError):
                record(state=invalid)
        with self.assertRaises(InvalidRecordError):
            record(steward_ref=None)


class LifecycleTest(unittest.TestCase):
    def test_each_axis_has_valid_transition(self) -> None:
        registered = record(
            asset_class="application",
            state=state(Maturity.REGISTERED, Publication.UNPUBLISHED, trust=Trust.T1),
        )
        promoted_trust = transition(registered, replace(registered.state, trust=Trust.T2))
        verified = transition(promoted_trust, replace(promoted_trust.state, maturity=Maturity.VERIFIED))
        published = transition(verified, replace(verified.state, publication=Publication.PUBLISHED))
        restricted = transition(published, replace(published.state, visibility=Visibility.RESTRICTED))
        self.assertEqual(restricted.state.visibility, Visibility.RESTRICTED)

    def test_invalid_transitions_are_semantic_errors(self) -> None:
        item = record()
        invalid = (
            replace(item.state, maturity=Maturity.OFFICIAL),
            replace(item.state, trust=Trust.T4),
            replace(item.state, visibility=Visibility.PUBLIC),
            replace(item.state, maturity=Maturity.CURATED, trust=Trust.T3),
        )
        for target in invalid:
            with self.subTest(target=target), self.assertRaises(InvalidLifecycleTransitionError):
                transition(item, target)

    def test_terminal_publication_states_do_not_restore(self) -> None:
        withdrawn = record(state=state(publication=Publication.WITHDRAWN))
        with self.assertRaises(InvalidLifecycleTransitionError):
            transition(withdrawn, replace(withdrawn.state, publication=Publication.PUBLISHED))


class NegotiationTest(unittest.TestCase):
    def test_supported_version_and_capability_intersection(self) -> None:
        local = CapabilityProfile((FCPVersion(1, 2), FCPVersion(1, 0)), ("conformance", "records"))
        remote = CapabilityProfile((FCPVersion(1, 1),), ("records", "discovery"))
        result = negotiate(local, remote)
        self.assertEqual(result.version, FCPVersion(1, 1))
        self.assertEqual(result.capabilities, ("records",))
        self.assertTrue(result.downgraded)

    def test_incompatible_major_fails(self) -> None:
        with self.assertRaises(UnsupportedVersionError):
            negotiate(CapabilityProfile((FCPVersion(1, 0),), ()), CapabilityProfile((FCPVersion(2, 0),), ()))

    def test_required_capability_absence_fails(self) -> None:
        local = CapabilityProfile((FCPVersion(1, 0),), ("records",), ("records",))
        remote = CapabilityProfile((FCPVersion(1, 0),), ("conformance",))
        with self.assertRaises(CapabilityAbsentError):
            negotiate(local, remote)

    def test_downgrade_can_be_refused(self) -> None:
        local = CapabilityProfile((FCPVersion(1, 2),), ("records",))
        remote = CapabilityProfile((FCPVersion(1, 1),), ("records",))
        with self.assertRaises(UnsupportedVersionError):
            negotiate(local, remote, allow_minor_downgrade=False)


class EnvelopeTest(unittest.TestCase):
    def test_valid_read_only_envelope(self) -> None:
        issued = datetime(2026, 1, 1, tzinfo=UTC)
        envelope = OperationEnvelope(
            "op:synthetic:1", "corr:synthetic:1", FCPVersion(1, 0), ("records",),
            "actor:technical:synthetic", None, "test", "testers", "authz:synthetic",
            issued, issued + timedelta(seconds=5), ("scope:synthetic",),
            ("policy:synthetic",), True, PageRequest(10, "sha256:synthetic"),
        )
        self.assertTrue(envelope.read_only)

    def test_envelope_rejects_writes_and_bad_deadline(self) -> None:
        issued = datetime(2026, 1, 1, tzinfo=UTC)
        base = ["op", "corr", FCPVersion(1, 0), (), "actor", None, "purpose", "audience", "authz", issued]
        with self.assertRaises(InvalidEnvelopeError):
            OperationEnvelope(*base, issued, ("scope",), ("policy",), True)
        with self.assertRaises(InvalidEnvelopeError):
            OperationEnvelope(*base, issued + timedelta(seconds=1), ("scope",), ("policy",), False)
        with self.assertRaises(InvalidEnvelopeError):
            PageRequest(True, "scope")  # type: ignore[arg-type]


class SerializationAndIsolationTest(unittest.TestCase):
    def test_golden_fixture_and_repeated_determinism(self) -> None:
        item = record()
        expected = (FIXTURES / "valid_record.json").read_text(encoding="utf-8").strip()
        outputs = {canonical_json(item) for _ in range(100)}
        self.assertEqual(outputs, {expected})
        self.assertEqual(len({canonical_digest(item) for _ in range(100)}), 1)

    def test_semantically_identical_mapping_order_is_canonical(self) -> None:
        self.assertEqual(canonical_json({"b": 2, "a": 1}), canonical_json({"a": 1, "b": 2}))

    def test_domain_has_no_io_core_or_network_imports(self) -> None:
        forbidden = {"cko", "pathlib", "socket", "urllib", "http", "requests", "subprocess", "sqlite3"}
        for path in (Path(__file__).parents[1] / "src" / "cko_fcp").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            roots = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    roots.add(node.module.split(".")[0])
            self.assertFalse(roots & forbidden, f"forbidden dependency in {path}: {roots & forbidden}")

    def test_validation_performs_no_io(self) -> None:
        with patch("builtins.open", side_effect=AssertionError("I/O attempted")), patch("socket.socket", side_effect=AssertionError("network attempted")):
            self.assertEqual(canonical_json(record()), (FIXTURES / "valid_record.json").read_text(encoding="utf-8").strip())

    def test_negative_fixture_codes_are_covered(self) -> None:
        vectors = json.loads((FIXTURES / "invalid_vectors.json").read_text(encoding="utf-8"))
        self.assertEqual(
            {item["expected_code"] for item in vectors},
            {"FCP_INVALID_INPUT", "FCP_UNSUPPORTED_MAJOR", "FCP_CAPABILITY_ABSENT", "FCP_ILLEGAL_TRANSITION"},
        )


if __name__ == "__main__":
    unittest.main()
