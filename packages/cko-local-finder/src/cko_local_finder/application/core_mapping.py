"""Pure declarative mapping to Core concepts without importing Core."""

from cko_local_finder.domain.models import CoreDocumentMapping, CoreProvenanceMapping, DocumentProvenance


def map_core_document(value: DocumentProvenance) -> CoreDocumentMapping:
    return CoreDocumentMapping(value.sha256, value.media_type, value.size_bytes,
                               tuple((origin.root, origin.relative_path) for origin in value.origins))


def map_core_provenance(value: DocumentProvenance) -> CoreProvenanceMapping:
    return CoreProvenanceMapping(
        value.sha256,
        tuple((origin.root, origin.relative_path) for origin in value.origins),
        value.extraction.status if value.extraction else None,
        "extracted_text" if value.extraction else None,
        tuple(issue.code for issue in value.issues),
        len(value.duplicate.origins) if value.duplicate else 0,
    )
