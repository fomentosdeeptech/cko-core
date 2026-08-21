import pytest
from cko_local_finder.infrastructure.text import TextLimitError,normalize_text

def test_bom_newlines_nfc_and_paragraphs():
    assert normalize_text("\ufeffA\r\n\r\ne\u0301\rB\n",max_characters=20)=="A\n\né\nB\n"

def test_no_semantic_whitespace_collapse():
    assert normalize_text("a  b\n\n c ",max_characters=20)=="a  b\n\n c "

def test_limit_is_explicit_without_truncation():
    with pytest.raises(TextLimitError) as error: normalize_text("abcd",max_characters=3)
    assert error.value.observed==4
