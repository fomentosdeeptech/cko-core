"""Application service for explainable document provenance."""

from cko_local_finder.application.ports import ProvenancePort
from cko_local_finder.domain.models import ProvenanceBundle


def provenance_for_sha256(sha256: str, repository: ProvenancePort) -> ProvenanceBundle:
    if len(sha256) != 64 or any(char not in "0123456789abcdef" for char in sha256):
        raise ValueError("invalid SHA-256")
    repository.apply_provenance_migrations()
    result = repository.provenance_by_sha256(sha256)
    if result is None:
        raise LookupError("document provenance not found")
    return result


def provenance_for_location(root: str, relative_path: str, repository: ProvenancePort) -> ProvenanceBundle:
    if not root or not relative_path:
        raise ValueError("root and relative_path are required")
    repository.apply_provenance_migrations()
    result = repository.provenance_by_location(root, relative_path)
    if result is None:
        raise LookupError("document provenance not found")
    return result
