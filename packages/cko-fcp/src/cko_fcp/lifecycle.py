"""Validation for independent maturity, publication, visibility, and trust axes."""

from __future__ import annotations

from dataclasses import replace

from .errors import InvalidLifecycleTransitionError
from .models import CatalogRecord, Maturity, Publication, RecordState, Trust, Visibility


_MATURITY_NEXT = {
    Maturity.LOCATED: {Maturity.REGISTERED},
    Maturity.REGISTERED: {Maturity.VERIFIED},
    Maturity.VERIFIED: {Maturity.CURATED},
    Maturity.CURATED: {Maturity.OFFICIAL},
    Maturity.OFFICIAL: set(),
}
_TRUST_NEXT = {
    Trust.T0: {Trust.T1}, Trust.T1: {Trust.T2}, Trust.T2: {Trust.T3},
    Trust.T3: {Trust.T4}, Trust.T4: set(),
}
_VISIBILITY_RANK = {
    Visibility.PUBLIC: 0, Visibility.INSTITUTIONAL: 1,
    Visibility.RESTRICTED: 2, Visibility.EXISTENCE_RESTRICTED: 3,
}


def transition(record: CatalogRecord, target: RecordState) -> CatalogRecord:
    """Return a successor record after validating a single governed state change."""
    if not isinstance(record, CatalogRecord) or not isinstance(target, RecordState):
        raise InvalidLifecycleTransitionError("transition requires a record and target state")
    current = record.state
    changed = [name for name in ("maturity", "publication", "visibility", "trust") if getattr(current, name) != getattr(target, name)]
    if len(changed) != 1:
        raise InvalidLifecycleTransitionError("a transition must change exactly one state axis")
    axis = changed[0]
    if axis == "maturity" and target.maturity not in _MATURITY_NEXT[current.maturity]:
        raise InvalidLifecycleTransitionError("illegal maturity transition")
    if axis == "trust" and target.trust not in _TRUST_NEXT[current.trust]:
        raise InvalidLifecycleTransitionError("illegal trust transition")
    if axis == "visibility" and _VISIBILITY_RANK[target.visibility] < _VISIBILITY_RANK[current.visibility]:
        raise InvalidLifecycleTransitionError("P-018-01 permits restriction but not access expansion")
    if axis == "publication":
        allowed = {
            Publication.UNPUBLISHED: {Publication.PUBLISHED, Publication.REJECTED, Publication.SUSPENDED},
            Publication.PUBLISHED: {Publication.SUSPENDED, Publication.WITHDRAWN},
            Publication.SUSPENDED: {Publication.UNPUBLISHED, Publication.PUBLISHED, Publication.WITHDRAWN},
            Publication.WITHDRAWN: set(), Publication.REJECTED: set(),
        }
        if target.publication not in allowed[current.publication]:
            raise InvalidLifecycleTransitionError("illegal publication transition")
    try:
        return replace(record, state=target)
    except Exception as exc:
        if isinstance(exc, InvalidLifecycleTransitionError):
            raise
        raise InvalidLifecycleTransitionError(str(exc)) from exc
