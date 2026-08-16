from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Protocol
import unittest

from cko_local_finder.application import ports
from cko_local_finder.domain.models import (
    ExtractionResult,
    ProcessingError,
    SearchResult,
    SourceFile,
)


def _source() -> SourceFile:
    return SourceFile("source-1", "documents/example.txt", "a" * 64, 12, "text/plain")


class ContractTest(unittest.TestCase):
    def test_four_models_construct_and_compare_deterministically(self) -> None:
        source = _source()
        extraction = ExtractionResult("source-1", "text", "plain", "1", (("encoding", "utf-8"),))
        result = SearchResult("source-1", 1.0, "text", source.path, source.sha256)
        error = ProcessingError("source-1", "extract", "invalid", "invalid input", True)
        self.assertEqual(source, _source())
        self.assertEqual(extraction.metadata, (("encoding", "utf-8"),))
        self.assertEqual(result.score, 1.0)
        self.assertTrue(error.recoverable)

    def test_models_are_frozen_and_slotted(self) -> None:
        models = (_source(), ExtractionResult("s", "", "e", "1"), SearchResult("s", 0.0, "", "p", "h"), ProcessingError("s", "x", "c", "m", False))
        for model in models:
            self.assertTrue(hasattr(type(model), "__slots__"))
            self.assertFalse(hasattr(model, "__dict__"))
            with self.assertRaises((FrozenInstanceError, AttributeError)):
                setattr(model, "source_id", "changed")

    def test_simple_structural_invariants(self) -> None:
        with self.assertRaisesRegex(ValueError, "size_bytes"):
            SourceFile("s", "p", "h", -1, "text/plain")
        with self.assertRaisesRegex(ValueError, "source_id"):
            ProcessingError("", "stage", "code", "message", True)

    def test_five_ports_are_protocols_without_concrete_bodies(self) -> None:
        expected = {"DiscoveryPort", "ExtractorPort", "DocumentRepositoryPort", "SearchIndexPort", "ProvenancePort"}
        self.assertEqual(expected, {name for name in expected if issubclass(getattr(ports, name), Protocol)})
        for name in expected:
            self.assertTrue(getattr(ports, name)._is_protocol)


if __name__ == "__main__":
    unittest.main()
