from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from cko_local_finder.application.facade import IngestRequest, ProgressEvent, ProgressStage, SearchRequest
from cko_local_finder.bootstrap import create_application
from cko_local_finder.cli.main import main


def test_facade_progress_and_immutable_dtos(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    root.mkdir()
    (root / "one.txt").write_text("shared facade token", encoding="utf-8")
    database = tmp_path / "finder.sqlite3"
    events: list[ProgressEvent] = []
    result = create_application().ingest(IngestRequest(str(root), str(database)), on_progress=events.append)
    assert result.successful_extractions == result.indexed_documents == 1
    assert [event.stage for event in events] == [
        ProgressStage.INGESTION_STARTED, ProgressStage.DISCOVERY_STARTED,
        ProgressStage.DISCOVERY_COMPLETED, ProgressStage.PERSISTENCE_STARTED,
        ProgressStage.PERSISTENCE_COMPLETED, ProgressStage.EXTRACTION_STARTED,
        ProgressStage.EXTRACTION_COMPLETED, ProgressStage.INDEXING_STARTED,
        ProgressStage.INDEXING_COMPLETED, ProgressStage.REPORTING_STARTED,
        ProgressStage.REPORTING_COMPLETED, ProgressStage.INGESTION_COMPLETED,
    ]
    with pytest.raises(FrozenInstanceError):
        events[0].count = 1  # type: ignore[misc]


def test_late_unexpected_failure_indexes_prior_successes(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "corpus"
    root.mkdir()
    (root / "a.txt").write_text("surviving searchable token", encoding="utf-8")
    (root / "b.txt").write_text("fails late", encoding="utf-8")
    database = tmp_path / "finder.sqlite3"
    from cko_local_finder.infrastructure import extractors

    original = extractors.PlainTextExtractor.extract

    def fail_second(self, source):
        if source.relative_path == "b.txt":
            raise RuntimeError("private document content and SELECT secret")
        return original(self, source)

    monkeypatch.setattr(extractors.PlainTextExtractor, "extract", fail_second)
    events: list[ProgressEvent] = []
    with pytest.raises(RuntimeError):
        create_application().ingest(IngestRequest(str(root), str(database)), on_progress=events.append)
    assert ProgressStage.EXTRACTION_COMPLETED not in [event.stage for event in events]
    assert events[-1].stage is ProgressStage.STAGE_FAILED
    out, err = __import__("io").StringIO(), __import__("io").StringIO()
    code = main(["search", "surviving", "--database", str(database)], stdout=out, stderr=err)
    assert code == 0 and "a.txt" in out.getvalue()
    assert "SELECT" not in err.getvalue() and "private document" not in err.getvalue()


def test_search_request_offset_defaults_to_zero_and_is_propagated(tmp_path: Path) -> None:
    root, database = tmp_path / "corpus", tmp_path / "finder.sqlite3"
    root.mkdir()
    for index, name in enumerate(("a.txt", "b.txt", "c.txt")):
        (root / name).write_text(f"pagination token {index}", encoding="utf-8")
    facade = create_application()
    facade.ingest(IngestRequest(str(root), str(database)))
    first = facade.search(SearchRequest("pagination", str(database), limit=1))
    second = facade.search(SearchRequest("pagination", str(database), limit=1, offset=1))
    assert first.offset == 0 and second.offset == 1
    assert first.results[0].sha256 != second.results[0].sha256


def test_successive_facade_pages_preserve_previous_search_behavior(tmp_path: Path) -> None:
    root, database = tmp_path / "corpus", tmp_path / "finder.sqlite3"
    root.mkdir()
    for index in range(5):
        (root / f"{index}.txt").write_text(f"shared page token {index}", encoding="utf-8")
    facade = create_application()
    facade.ingest(IngestRequest(str(root), str(database)))
    pages = [facade.search(SearchRequest("shared", str(database), limit=2, offset=offset))
             for offset in (0, 2, 4)]
    assert [len(page.results) for page in pages] == [2, 2, 1]
    assert len({item.sha256 for page in pages for item in page.results}) == 5
