"""Structural and cross-model validation for canonical knowledge corpora."""

from __future__ import annotations

from dataclasses import is_dataclass

from .contracts import CorpusModel
from .errors import CorpusDigestError, CorpusValidationError
from .models import (CorpusManifest, CorpusSnapshot, CorpusStatistics,
                     KnowledgeCorpus)


class CorpusValidator:
    def validate(self, value: CorpusModel, *, corpus: KnowledgeCorpus | None = None) -> None:
        if not isinstance(value, CorpusModel) or not is_dataclass(value):
            raise CorpusValidationError("value must be a canonical corpus dataclass")
        value._validate_schema()
        params = getattr(type(value), "__dataclass_params__", None)
        if params is None or not params.frozen or not hasattr(type(value), "__slots__"):
            raise CorpusValidationError("corpus models must be frozen and slotted")
        if value.model != type(value).discriminator:
            raise CorpusValidationError("invalid model discriminator")
        if isinstance(value, CorpusManifest):
            keys = [member.identity_key for member in value.members]
            if keys != sorted(keys):
                raise CorpusValidationError("manifest order is not canonical")
        elif isinstance(value, KnowledgeCorpus):
            from .factory import canonical_corpus_digest
            expected = canonical_corpus_digest(value.identity, value.corpus_version,
                                               value.manifest, value.metadata)
            if value.digest != expected:
                raise CorpusDigestError("corpus digest is invalid or content was altered")
        elif isinstance(value, CorpusSnapshot) and corpus is not None:
            if (value.corpus_id != corpus.identity.corpus_id or
                    value.corpus_version != corpus.corpus_version or
                    value.manifest != corpus.manifest or value.digest != corpus.digest):
                raise CorpusValidationError("snapshot is inconsistent with its corpus")
        elif isinstance(value, CorpusStatistics):
            if value.members_with_digest > value.total_members:
                raise CorpusValidationError("statistics digest count exceeds total members")


__all__ = ["CorpusValidator"]
