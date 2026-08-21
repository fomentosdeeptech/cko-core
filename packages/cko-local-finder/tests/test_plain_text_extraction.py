import hashlib
import pytest
from cko_local_finder.domain.models import DiscoveredFile,ExtractionPolicy
from cko_local_finder.infrastructure.extractors import ExtractionError,PlainTextExtractor

def source(path,extension=None):
    data=path.read_bytes(); d=hashlib.sha256(data).hexdigest()
    return DiscoveredFile(d,str(path),path.name,d,len(data),extension or path.suffix,1,"text/plain")

@pytest.mark.parametrize(("name","payload"),[("a.txt","olá\r\n".encode()),("a.md",b"# H\n"),("a.markdown",b"text"),("A.TXT",b"upper")])
def test_plain_formats_utf8_and_extension_case(tmp_path,name,payload):
    path=tmp_path/name; path.write_bytes(payload); result=PlainTextExtractor().extract(source(path))
    assert result.status=="SUCCESS" and "\r" not in result.text

def test_bom_empty_invalid_and_limits(tmp_path):
    bom=tmp_path/"bom.txt"; bom.write_bytes(b"\xef\xbb\xbfok")
    assert PlainTextExtractor().extract(source(bom)).text=="ok"
    empty=tmp_path/"empty.txt"; empty.write_bytes(b""); assert PlainTextExtractor().extract(source(empty)).status=="EMPTY"
    bad=tmp_path/"bad.txt"; bad.write_bytes(b"\xff")
    with pytest.raises(ExtractionError,match="UTF-8"): PlainTextExtractor().extract(source(bad))
    large=tmp_path/"large.txt"; large.write_bytes(b"abcd")
    with pytest.raises(ExtractionError) as error: PlainTextExtractor(ExtractionPolicy(max_source_file_size=3)).extract(source(large))
    assert error.value.code=="SOURCE_TOO_LARGE"

def test_character_limit_never_truncates(tmp_path):
    path=tmp_path/"a.txt"; path.write_text("abcd",encoding="utf-8")
    with pytest.raises(ExtractionError) as error: PlainTextExtractor(ExtractionPolicy(max_extracted_characters=3)).extract(source(path))
    assert error.value.code=="TEXT_TOO_LARGE" and error.value.observed_size==4
