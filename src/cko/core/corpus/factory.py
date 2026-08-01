"""Mandatory deterministic construction boundary for knowledge corpora."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Callable, Mapping

from .contracts import CORPUS_VERSION, primitive
from .enums import CorpusMemberCategory
from .errors import CorpusFactoryError, CorpusReferenceError
from .identity import CorpusId, CorpusIdentity
from .models import (_FACTORY_TOKEN, CorpusManifest, CorpusMemberReference,
                     CorpusMetadata, CorpusSnapshot, CorpusVersion,
                     KnowledgeCorpus)


def corpus_digest_payload(identity: CorpusIdentity, corpus_version: CorpusVersion,
                          manifest: CorpusManifest, metadata: CorpusMetadata) -> dict[str, object]:
    """Return the complete, non-self-referential payload covered by the corpus digest."""
    return {
        "schema_version": identity.schema_version,
        "serialization_version": "1.0",
        "identity": primitive(identity),
        "corpus_version": primitive(corpus_version),
        "manifest": primitive(manifest),
        "metadata": primitive(metadata),
    }


def canonical_corpus_digest(identity: CorpusIdentity, corpus_version: CorpusVersion,
                            manifest: CorpusManifest, metadata: CorpusMetadata) -> str:
    encoded = json.dumps(corpus_digest_payload(identity, corpus_version, manifest, metadata),
                         ensure_ascii=False, allow_nan=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def reference_from_member(member: object, *, member_digest: str | None = None,
                          attributes: Mapping[str, object] | None = None) -> CorpusMemberReference:
    """Create a minimal canonical reference from a supported public aggregate."""
    from cko.core.documents import CanonicalDocument, DeterministicDocumentSerializer
    from cko.core.graph import CanonicalGraph, DeterministicGraphSerializer
    from cko.core.index import CanonicalIndex, DeterministicIndexSerializer
    from cko.core.knowledge import KnowledgeObject, DeterministicKnowledgeSerializer
    from cko.core.query import CanonicalQuery
    from cko.core.relationships import CanonicalRelationship, DeterministicRelationshipSerializer

    if isinstance(member, CanonicalQuery):
        raise CorpusReferenceError("CanonicalQuery represents intent and cannot be a corpus member")
    if isinstance(member, KnowledgeObject):
        identity = member.identity
        return CorpusMemberReference(
            str(identity.canonical_id), CorpusMemberCategory.KNOWLEDGE_OBJECT,
            member.version.version, member.model, identity.namespace,
            (DeterministicKnowledgeSerializer().digest(member)
             if member_digest is None else member_digest), attributes or {})
    if isinstance(member, CanonicalDocument):
        identity = member.identity
        return CorpusMemberReference(
            str(identity.document_id), CorpusMemberCategory.CANONICAL_DOCUMENT,
            member.metadata.version, member.model, identity.namespace,
            (DeterministicDocumentSerializer().digest(member)
             if member_digest is None else member_digest), attributes or {})
    if isinstance(member, CanonicalRelationship):
        identity = member.identity
        return CorpusMemberReference(
            str(identity.canonical_id), CorpusMemberCategory.CANONICAL_RELATIONSHIP,
            member.version.version, member.model, identity.namespace,
            (DeterministicRelationshipSerializer().digest(member)
             if member_digest is None else member_digest), attributes or {})
    if isinstance(member, CanonicalGraph):
        identity = member.identity
        return CorpusMemberReference(
            str(identity.canonical_id), CorpusMemberCategory.CANONICAL_GRAPH,
            identity.version, member.model, identity.namespace,
            (DeterministicGraphSerializer().digest(member)
             if member_digest is None else member_digest), attributes or {})
    if isinstance(member, CanonicalIndex):
        identity = member.identity
        return CorpusMemberReference(
            str(identity.canonical_id), CorpusMemberCategory.CANONICAL_INDEX,
            member.version.version, member.model, identity.namespace,
            (DeterministicIndexSerializer().digest(member)
             if member_digest is None else member_digest), attributes or {})
    raise CorpusReferenceError("member is not an aggregate admitted by CorpusMemberCategory")


class CorpusFactory:
    def __init__(self, validator=None, clock: Callable[[], datetime] | None = None) -> None:
        from .validator import CorpusValidator
        self._validator = validator or CorpusValidator()
        self._clock = clock or (lambda: datetime.now(UTC))

    def create_reference(self, *, member_id: str, category: CorpusMemberCategory,
                         member_version: str, discriminator_name: str,
                         namespace: str, member_digest: str | None = None,
                         attributes: Mapping[str, object] | None = None) -> CorpusMemberReference:
        result = CorpusMemberReference(member_id, category, member_version,
                                       discriminator_name, namespace, member_digest,
                                       attributes or {})
        self._validator.validate(result)
        return result

    def reference_from_member(self, member: object, *, member_digest: str | None = None,
                              attributes: Mapping[str, object] | None = None) -> CorpusMemberReference:
        result = reference_from_member(member, member_digest=member_digest, attributes=attributes)
        self._validator.validate(result)
        return result

    def create_manifest(self, members: tuple[CorpusMemberReference, ...] = ()) -> CorpusManifest:
        result = CorpusManifest(members)
        self._validator.validate(result)
        return result

    def create_corpus(self, *, name: str, namespace: str,
                      members: tuple[CorpusMemberReference, ...] = (),
                      corpus_version: str = CORPUS_VERSION, revision: int = 0,
                      description: str | None = None, labels: tuple[str, ...] = (),
                      metadata: Mapping[str, object] | None = None) -> KnowledgeCorpus:
        identity = CorpusIdentity(CorpusId.canonical(namespace, name), namespace, name)
        version = CorpusVersion(corpus_version, revision)
        manifest = CorpusManifest(members)
        structural_metadata = CorpusMetadata(description, labels, metadata or {})
        return self.from_parts(identity=identity, corpus_version=version,
                               manifest=manifest, metadata=structural_metadata)

    def from_parts(self, *, identity: CorpusIdentity, corpus_version: CorpusVersion,
                   manifest: CorpusManifest, metadata: CorpusMetadata,
                   digest: str | None = None) -> KnowledgeCorpus:
        expected = canonical_corpus_digest(identity, corpus_version, manifest, metadata)
        if digest is not None and digest.lower() != expected:
            from .errors import CorpusDigestError
            raise CorpusDigestError("corpus digest is invalid or content was altered")
        result = KnowledgeCorpus(identity, corpus_version, manifest, metadata,
                                 expected, _factory_token=_FACTORY_TOKEN)
        self._validator.validate(result)
        return result

    def create_snapshot(self, corpus: KnowledgeCorpus, *,
                        captured_at: datetime | None = None) -> CorpusSnapshot:
        from .operations import corpus_statistics
        if not isinstance(corpus, KnowledgeCorpus):
            raise CorpusFactoryError("corpus must be KnowledgeCorpus")
        snapshot_id = CorpusId.canonical(
            corpus.identity.namespace,
            f"snapshot:{corpus.identity.corpus_id}:{corpus.corpus_version.version}:"
            f"{corpus.corpus_version.revision}:{corpus.digest}")
        result = CorpusSnapshot(snapshot_id, corpus.identity.corpus_id,
                                corpus.corpus_version, corpus.manifest, corpus.digest,
                                corpus_statistics(corpus), captured_at or self._clock())
        self._validator.validate(result, corpus=corpus)
        return result


__all__ = [
    "CorpusFactory", "canonical_corpus_digest", "corpus_digest_payload",
    "reference_from_member",
]
