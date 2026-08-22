import ast
from pathlib import Path
from cko_local_finder.application.core_mapping import map_core_document,map_core_provenance
from tests.test_provenance import seeded

def test_pure_deterministic_core_mappings_without_core_import(tmp_path):
    repo,d=seeded(tmp_path); value=repo.provenance_by_sha256(d).document
    assert map_core_document(value)==map_core_document(value)
    assert map_core_provenance(value)==map_core_provenance(value)
    path=Path(__file__).parents[1]/"src"/"cko_local_finder"/"application"/"core_mapping.py"
    imports={n.module.split('.')[0] for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.ImportFrom) and n.module}
    assert "cko" not in imports
