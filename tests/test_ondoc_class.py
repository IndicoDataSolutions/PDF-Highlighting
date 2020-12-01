"""
Test OnDoc class object
"""
import pytest
from highlighter import OnDoc


def test_ondoc_properties(full_ondoc_ocr):
    ocr = OnDoc(full_ondoc_ocr)
    full_text = ocr.full_text
    assert isinstance(full_text, str)
    page_text = ocr.page_text
    assert isinstance(page_text, list)
    assert len(page_text) == 2
    assert page_text[0] in full_text and page_text[1] in full_text
    block_text = ocr.block_text
    assert isinstance(block_text, list)
    assert block_text[0] in page_text[0]
    assert block_text[-1] in page_text[-1]
    page_objects = ocr.page_results
    assert len(page_objects) == 2
    assert isinstance(page_objects[0], dict)
    assert "text" and "page_num" and "size" in page_objects[0].keys()
    with pytest.raises(Exception):
        ocr.ocr_confidence() # Old OCR version doesn't include confidence
