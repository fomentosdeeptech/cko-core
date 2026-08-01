from pathlib import Path

from cko.metadata.file_metadata import classify_by_extension, collect_metadata, is_temporary


def test_classification():
    assert classify_by_extension(Path("arquivo.pdf")) == "PDF"
    assert classify_by_extension(Path("imagem.png")) == "Imagem"
    assert classify_by_extension(Path("dados.xlsx")) == "Planilha"
    assert classify_by_extension(Path("codigo.py")) == "Código"


def test_temporary_detection():
    assert is_temporary(Path("arquivo.tmp"))
    assert is_temporary(Path("~$documento.docx"))
    assert not is_temporary(Path("documento.pdf"))


def test_collect_metadata(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("CKO", encoding="utf-8")

    metadata = collect_metadata(sample, source_root=tmp_path)

    assert metadata.name == "sample.txt"
    assert metadata.extension == ".txt"
    assert metadata.size_bytes == 3
    assert metadata.sha256
    assert metadata.category == "Texto"
