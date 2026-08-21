import hashlib
import pytest
from pypdf import PdfWriter
from tests.corpus_factory import _minimal_pdf
from cko_local_finder.domain.models import DiscoveredFile
from cko_local_finder.infrastructure.extractors import ExtractionError,PdfTextExtractor

def source(path):
    b=path.read_bytes(); d=hashlib.sha256(b).hexdigest(); return DiscoveredFile(d,str(path),path.name,d,len(b),".pdf",1,"application/pdf")

def test_textual_pdf_metadata_and_determinism(tmp_path):
    path=tmp_path/"a.pdf"; path.write_bytes(_minimal_pdf()); extractor=PdfTextExtractor()
    first=extractor.extract(source(path)); second=extractor.extract(source(path))
    assert "Synthetic local" in first.text and first==second and dict(first.metadata)["pages"]=="1"

def test_no_text_pdf_has_explicit_status(tmp_path):
    path=tmp_path/"empty.pdf"; writer=PdfWriter(); writer.add_blank_page(100,100)
    with path.open("wb") as output: writer.write(output)
    result=PdfTextExtractor().extract(source(path)); assert result.status=="NO_TEXT" and result.text==""

def test_corrupt_pdf_is_recoverable_error(tmp_path):
    path=tmp_path/"bad.pdf"; path.write_bytes(b"%PDF-bad")
    with pytest.raises(ExtractionError) as error: PdfTextExtractor().extract(source(path))
    assert error.value.code=="CORRUPT_PDF"

def test_encrypted_pdf_status(tmp_path):
    path=tmp_path/"encrypted.pdf"; writer=PdfWriter(); writer.add_blank_page(100,100); writer.encrypt("secret")
    with path.open("wb") as output: writer.write(output)
    with pytest.raises(ExtractionError) as error: PdfTextExtractor().extract(source(path))
    assert error.value.code=="ENCRYPTED"
