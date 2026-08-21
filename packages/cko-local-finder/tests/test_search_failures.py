import sqlite3
import pytest
from cko_local_finder.domain.models import SearchQuery
from cko_local_finder.infrastructure.search import SearchError
from cko_local_finder.infrastructure.sqlite import RepositoryError,SQLiteDocumentRepository
from tests.test_text_indexing import seeded_repo

def test_closed_corrupt_and_uninitialized_database_errors(tmp_path):
    path=tmp_path/"bad.db"; path.write_bytes(b"bad")
    with pytest.raises(RepositoryError): SQLiteDocumentRepository(path).apply_search_migrations()
    repo=SQLiteDocumentRepository(tmp_path/"plain.db"); repo.apply_migrations()
    with pytest.raises(RepositoryError,match="search operation failed"): repo.search(SearchQuery("term"))

def test_index_failure_has_no_partial_state(tmp_path):
    repo,files=seeded_repo(tmp_path)
    with repo.connection() as db:
        db.execute("DROP TRIGGER search_index_ai")
        db.execute("CREATE TRIGGER search_index_ai BEFORE INSERT ON search_index_documents BEGIN SELECT RAISE(ABORT,'controlled'); END")
    with pytest.raises(sqlite3.IntegrityError): repo.index_document(files[0].sha256,"t")
    with repo.connection() as db: assert db.execute("SELECT count(*) FROM search_index_documents").fetchone()[0]==0

def test_status_reports_rebuild_requirement(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); repo.apply_migrations()
    assert repo.search_index_status().rebuild_required
