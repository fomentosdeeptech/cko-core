"""Closed and versioned member categories admitted by a knowledge corpus."""

from enum import Enum


class CorpusMemberCategory(str, Enum):
    KNOWLEDGE_OBJECT = "knowledge_object"
    CANONICAL_DOCUMENT = "canonical_document"
    CANONICAL_RELATIONSHIP = "canonical_relationship"
    CANONICAL_GRAPH = "canonical_graph"
    CANONICAL_INDEX = "canonical_index"


__all__ = ["CorpusMemberCategory"]
