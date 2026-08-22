"""Stable human-readable and deterministic JSON presentation."""
from __future__ import annotations
from dataclasses import asdict, is_dataclass
import json
from typing import Any
from cko_local_finder.domain.models import DuplicateReport, ProvenanceBundle, SearchPage
from cko_local_finder.cli.runtime import IngestResult

def json_output(value: Any) -> str:
    payload = asdict(value) if is_dataclass(value) else value
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"

def text_output(value: Any) -> str:
    if isinstance(value, IngestResult):
        fields = (("Root", value.root), ("Database", value.database),
                  ("Documents discovered", value.discovered_documents), ("Unique documents", value.unique_documents),
                  ("Locations", value.locations), ("Duplicate groups", value.duplicate_groups),
                  ("Successful extractions", value.successful_extractions),
                  ("Recoverable failures", value.recoverable_failures), ("Documents indexed", value.indexed_documents))
        lines = [f"{key}: {item}" for key, item in fields]
    elif isinstance(value, SearchPage):
        lines = [f"Matches: {value.total_matches}"]
        for position, item in enumerate(value.results, 1):
            lines.extend((f"[{position}] {item.title or item.path}", f"Score: {item.score}", f"Root: {item.root}",
                          f"Path: {item.path}", f"SHA-256: {item.sha256}", f"Snippet: {item.snippet}"))
    elif isinstance(value, ProvenanceBundle):
        document = value.document
        lines = [f"SHA-256: {document.sha256}", f"Type: {document.media_type}", f"Size: {document.size_bytes}",
                 f"Extraction: {document.extraction.status if document.extraction else 'NOT_PROCESSED'}",
                 f"Indexed: {'YES' if document.indexing.indexed else 'NO'}",
                 f"Duplicate: {'YES' if document.duplicate else 'NO'}", "Locations:"]
        lines.extend(f"- {origin.root} :: {origin.relative_path}" for origin in document.origins)
        lines.append("Issues:")
        lines.extend(f"- {issue.stage}/{issue.code}: {issue.message}" for issue in document.issues)
        if not document.issues: lines.append("- none")
    elif isinstance(value, DuplicateReport):
        lines = [f"Duplicate groups: {len(value.duplicates)}"]
        for item in value.duplicates:
            lines.extend((f"SHA-256: {item.sha256}", f"Locations: {len(item.origins)}"))
            lines.extend(f"- {origin.root} :: {origin.relative_path}" for origin in item.origins)
    elif is_dataclass(value):
        lines = [f"{key}: {json.dumps(item, ensure_ascii=False, sort_keys=True)}" for key, item in asdict(value).items()]
    else: lines = [str(value)]
    return "\n".join(lines) + "\n"

def present(value: Any, output_format: str) -> str:
    return json_output(value) if output_format == "json" else text_output(value)
