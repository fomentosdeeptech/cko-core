"""Pure deterministic structural operations over knowledge corpora."""

from __future__ import annotations

from collections import Counter

from .enums import CorpusMemberCategory
from .errors import CorpusOperationError, DuplicateCorpusMemberError
from .models import (CorpusComparisonResult, CorpusMemberReference,
                     CorpusReferenceChange, CorpusStatistics, KnowledgeCorpus)


def _key(value: CorpusMemberReference | tuple[CorpusMemberCategory | str, str, str]) -> tuple[str, str, str]:
    if isinstance(value, CorpusMemberReference):
        return value.identity_key
    category, namespace, member_id = value
    return (CorpusMemberCategory(category).value, namespace, member_id)


def contains_member(corpus: KnowledgeCorpus,
                    reference: CorpusMemberReference | tuple[CorpusMemberCategory | str, str, str]) -> bool:
    selected = _key(reference)
    return any(member.identity_key == selected for member in corpus.manifest.members)


def find_member(corpus: KnowledgeCorpus, category: CorpusMemberCategory | str,
                namespace: str, member_id: str) -> CorpusMemberReference | None:
    selected = _key((category, namespace, member_id))
    return next((member for member in corpus.manifest.members if member.identity_key == selected), None)


def filter_members(corpus: KnowledgeCorpus,
                   category: CorpusMemberCategory | str) -> tuple[CorpusMemberReference, ...]:
    selected = CorpusMemberCategory(category)
    return tuple(member for member in corpus.manifest.members if member.category is selected)


def _rebuild(corpus: KnowledgeCorpus, members: tuple[CorpusMemberReference, ...]) -> KnowledgeCorpus:
    from .factory import CorpusFactory
    return CorpusFactory().from_parts(
        identity=corpus.identity,
        corpus_version=type(corpus.corpus_version)(corpus.corpus_version.version,
                                                   corpus.corpus_version.revision + 1),
        manifest=type(corpus.manifest)(members), metadata=corpus.metadata)


def add_member(corpus: KnowledgeCorpus, reference: CorpusMemberReference) -> KnowledgeCorpus:
    if not isinstance(reference, CorpusMemberReference):
        raise CorpusOperationError("reference must be CorpusMemberReference")
    if contains_member(corpus, reference):
        raise DuplicateCorpusMemberError("member identity already belongs to the corpus")
    return _rebuild(corpus, (*corpus.manifest.members, reference))


def remove_member(corpus: KnowledgeCorpus,
                  reference: CorpusMemberReference | tuple[CorpusMemberCategory | str, str, str]) -> KnowledgeCorpus:
    selected = _key(reference)
    remaining = tuple(member for member in corpus.manifest.members if member.identity_key != selected)
    if len(remaining) == len(corpus.manifest.members):
        raise CorpusOperationError("member identity does not belong to the corpus")
    return _rebuild(corpus, remaining)


def compare_corpora(before: KnowledgeCorpus, after: KnowledgeCorpus) -> CorpusComparisonResult:
    left = {member.identity_key: member for member in before.manifest.members}
    right = {member.identity_key: member for member in after.manifest.members}
    added = tuple(right[key] for key in right.keys() - left.keys())
    removed = tuple(left[key] for key in left.keys() - right.keys())
    preserved: list[CorpusMemberReference] = []
    changed: list[CorpusReferenceChange] = []
    for key in left.keys() & right.keys():
        old, new = left[key], right[key]
        if old == new:
            preserved.append(old)
        else:
            changed.append(CorpusReferenceChange(
                old, new, old.member_version != new.member_version,
                old.member_digest != new.member_digest))
    return CorpusComparisonResult(added, removed, tuple(preserved), tuple(changed))


def corpus_statistics(corpus: KnowledgeCorpus) -> CorpusStatistics:
    members = corpus.manifest.members
    by_category = Counter(member.category.value for member in members)
    by_version = Counter(member.member_version for member in members)
    return CorpusStatistics(
        len(members), sum(member.member_digest is not None for member in members),
        len(by_category), dict(sorted(by_category.items())),
        dict(sorted(by_version.items())))


class CorpusOperations:
    """Namespaced façade for the pure operation functions."""

    add = staticmethod(add_member)
    remove = staticmethod(remove_member)
    contains = staticmethod(contains_member)
    find = staticmethod(find_member)
    filter = staticmethod(filter_members)
    compare = staticmethod(compare_corpora)
    statistics = staticmethod(corpus_statistics)


__all__ = [
    "CorpusOperations", "add_member", "compare_corpora", "contains_member",
    "corpus_statistics", "filter_members", "find_member", "remove_member",
]
