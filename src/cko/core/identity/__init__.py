"""Identidade, versão e origem canônicas."""

from .identifier import CanonicalId
from .origin import Origin
from .version import SemanticVersion

__all__ = ["CanonicalId", "Origin", "SemanticVersion"]

