"""In-memory construction helper that produces new immutable corpora."""

from __future__ import annotations

from typing import Mapping

from .errors import CorpusOperationError, DuplicateCorpusMemberError
from .factory import CorpusFactory
from .models import CorpusMemberReference, KnowledgeCorpus


class CorpusBuilder:
    def __init__(self, *, name: str, namespace: str,
                 corpus_version: str = "1.0.0", revision: int = 0,
                 description: str | None = None, labels: tuple[str, ...] = (),
                 metadata: Mapping[str, object] | None = None,
                 factory: CorpusFactory | None = None) -> None:
        self._factory = factory or CorpusFactory()
        self._name = name
        self._namespace = namespace
        self._version = corpus_version
        self._revision = revision
        self._description = description
        self._labels = labels
        self._metadata = metadata or {}
        self._members: dict[tuple[str, str, str], CorpusMemberReference] = {}

    @classmethod
    def from_corpus(cls, corpus: KnowledgeCorpus,
                    factory: CorpusFactory | None = None) -> "CorpusBuilder":
        if not isinstance(corpus, KnowledgeCorpus):
            raise CorpusOperationError("corpus must be KnowledgeCorpus")
        builder = cls(name=corpus.identity.name, namespace=corpus.identity.namespace,
                      corpus_version=corpus.corpus_version.version,
                      revision=corpus.corpus_version.revision + 1,
                      description=corpus.metadata.description,
                      labels=corpus.metadata.labels,
                      metadata=dict(corpus.metadata.attributes), factory=factory)
        builder._members = {member.identity_key: member for member in corpus.manifest.members}
        return builder

    def add_reference(self, reference: CorpusMemberReference) -> "CorpusBuilder":
        if not isinstance(reference, CorpusMemberReference):
            raise CorpusOperationError("reference must be CorpusMemberReference")
        if reference.identity_key in self._members:
            raise DuplicateCorpusMemberError("member identity is duplicated")
        self._members[reference.identity_key] = reference
        return self

    def add(self, member: object, **reference_options) -> "CorpusBuilder":
        return self.add_reference(self._factory.reference_from_member(member, **reference_options))

    def remove_reference(self, reference: CorpusMemberReference) -> "CorpusBuilder":
        if self._members.pop(reference.identity_key, None) is None:
            raise CorpusOperationError("member identity is not present")
        return self

    def build(self) -> KnowledgeCorpus:
        return self._factory.create_corpus(
            name=self._name, namespace=self._namespace,
            members=tuple(self._members.values()), corpus_version=self._version,
            revision=self._revision, description=self._description,
            labels=self._labels, metadata=self._metadata)


__all__ = ["CorpusBuilder"]
